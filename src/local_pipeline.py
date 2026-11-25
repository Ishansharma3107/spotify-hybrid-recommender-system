"""Build reproducible local artifacts from the two original CSV schemas."""
import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix, save_npz
from sklearn.preprocessing import MinMaxScaler

from src.recommender import AUDIO, CATALOG, FEATURES, INTERACTIONS, METRICS, ROOT, Recommender

SOURCE = ("https://www.kaggle.com/api/v1/datasets/download/"
          "undefinenull/million-song-dataset-spotify-lastfm/")
RAW = ROOT / "data/raw"
MUSIC = "Music Info.csv"
HISTORY = "User Listening History.csv"
LOCAL_HISTORY = CATALOG.with_name("listens.csv")
HASHES = {MUSIC: "e63b74919a3cdada5c804df4666391c9",
          HISTORY: "3a12e713844195171c7040c051d6d4ae"}


def acquire():
    for filename, expected in HASHES.items():
        target = RAW / filename
        if target.exists():
            continue
        with tempfile.TemporaryDirectory(dir=RAW) as directory:
            archive = Path(directory) / "download.zip"
            staged = Path(directory) / filename
            with urllib.request.urlopen(SOURCE + quote(filename), timeout=120) as response:
                with archive.open("wb") as output:
                    shutil.copyfileobj(response, output)
            with zipfile.ZipFile(archive) as zipped, zipped.open(filename) as source:
                with staged.open("wb") as output:
                    shutil.copyfileobj(source, output)
            with staged.open("rb") as data:
                actual = hashlib.file_digest(data, "md5").hexdigest()
            if actual != expected:
                raise ValueError(f"Upstream checksum mismatch for {filename}: {actual}")
            staged.replace(target)


def preprocess():
    tracks = pd.read_csv(RAW / MUSIC)
    tracks = tracks.dropna(subset=["track_id", "name", "artist"]).drop_duplicates("track_id")
    tracks = tracks.sort_values("track_id").reset_index(drop=True)
    for column in AUDIO:
        numeric = pd.to_numeric(tracks[column], errors="coerce")
        tracks[column] = numeric.fillna(numeric.median()).fillna(0)
    tracks["genre"] = tracks.genre.fillna("Unknown").replace("", "Unknown")
    tracks["mood"] = np.select(
        [(tracks.energy >= .65) & (tracks.valence >= .55), tracks.energy >= .7,
         tracks.energy <= .35, tracks.valence < .4],
        ["Upbeat", "Energetic", "Calm", "Melancholic"], default="Balanced")
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    tracks[["track_id", "name", "artist", "genre", "mood", "spotify_preview_url", *AUDIO]].to_csv(
        CATALOG, index=False)
    # Hash-sample complete user histories. Chunking bounds peak memory.
    chunks = []
    for chunk in pd.read_csv(RAW / HISTORY, chunksize=200_000,
                             usecols=["track_id", "user_id", "playcount"]):
        chunk = chunk.dropna()
        users = chunk.user_id.astype(str)
        bucket = pd.util.hash_pandas_object(users, index=False) % 50
        chunk = chunk[(bucket == 0) & chunk.track_id.isin(tracks.track_id) & (chunk.playcount > 0)]
        if not chunk.empty:
            chunks.append(chunk)
    if not chunks:
        raise ValueError("No matching user histories found.")
    pd.concat(chunks).groupby(["user_id", "track_id"], as_index=False).playcount.sum().to_csv(
        LOCAL_HISTORY, index=False)


def features():
    tracks = pd.read_csv(CATALOG)
    audio = MinMaxScaler().fit_transform(tracks[AUDIO])
    np.save(FEATURES, audio.astype("float32"))


def matrix(tracks, listens, users):
    rows = pd.Index(tracks.track_id).get_indexer(listens.track_id)
    cols = users.get_indexer(listens.user_id)
    values = np.log1p(listens.playcount.to_numpy(dtype="float32"))
    return coo_matrix((values, (rows, cols)), shape=(len(tracks), len(users))).tocsr()


def train():
    tracks = pd.read_csv(CATALOG)
    listens = pd.read_csv(LOCAL_HISTORY)
    save_npz(INTERACTIONS, matrix(tracks, listens, pd.Index(listens.user_id.unique())))


def evaluate():
    tracks = pd.read_csv(CATALOG, keep_default_na=False)
    listens = pd.read_csv(LOCAL_HISTORY)
    # Split by whole user so none of the test profiles inform item similarities.
    users = pd.Index(sorted(listens.user_id.unique()))
    rng = np.random.default_rng(42)
    test_users = rng.permutation(users.to_numpy())[:max(1, len(users) // 5)]
    train_rows = listens[~listens.user_id.isin(test_users)]
    train_users = pd.Index(train_rows.user_id.unique())
    model = Recommender(tracks, np.load(FEATURES), matrix(tracks, train_rows, train_users))
    profiles = listens[listens.user_id.isin(test_users)].groupby("user_id").track_id.agg(list)
    totals = {mode: np.zeros(3) for mode in ["Popular", "Content", "Collaborative", "Hybrid"]}
    count = 0
    for profile in profiles:
        if len(profile) < 2:
            continue
        seed, target = rng.choice(profile, size=2, replace=False)
        count += 1
        hidden = set(profile) - {target}
        for mode, total in totals.items():
            ranked = model.recommend(seed, mode, k=10, hidden=hidden).track_id.tolist()
            if target in ranked:
                rank = ranked.index(target) + 1
                total += [1, 1 / rank, 1 / np.log2(rank + 1)]
    if not count:
        raise ValueError("The evaluation requires test users with at least two tracks.")
    scores = {mode: dict(zip(("Recall@10", "MRR@10", "NDCG@10"), (total / count).tolist()))
              for mode, total in totals.items()}
    METRICS.write_text(json.dumps({"test_profiles": count, "seed": 42, "models": scores}, indent=2),
                       encoding="utf-8")


if __name__ == "__main__":
    stages = {"acquire": acquire, "preprocess": preprocess, "features": features,
              "train": train, "evaluate": evaluate}
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=[*stages, "all"])
    stage = parser.parse_args().stage
    if stage == "all":
        for action in stages.values():
            action()
    else:
        stages[stage]()
