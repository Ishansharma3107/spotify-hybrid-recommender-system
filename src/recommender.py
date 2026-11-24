"""Track-ID aligned item-to-item recommendation models."""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from sklearn.preprocessing import minmax_scale, normalize

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/local/catalog.csv"
FEATURES = ROOT / "data/local/audio.npy"
INTERACTIONS = ROOT / "data/local/interactions.npz"
METRICS = ROOT / "reports/model_metrics.json"
AUDIO = ["danceability", "energy", "speechiness", "acousticness",
         "instrumentalness", "liveness", "valence", "tempo", "loudness"]


class Recommender:
    def __init__(self, catalog, audio, interactions):
        self.catalog = catalog
        self.audio = audio
        self.interactions = interactions.tocsr()
        if len(catalog) != len(audio) or len(catalog) != interactions.shape[0]:
            raise ValueError("Track catalog and model artifacts are misaligned.")
        self.popularity = interactions.getnnz(axis=1)
        self.audio_unit = normalize(audio)
        self.interaction_unit = normalize(self.interactions)
        self.indices = {track_id: i for i, track_id in enumerate(catalog.track_id)}

    @classmethod
    def load(cls):
        return cls(pd.read_csv(CATALOG, keep_default_na=False),
                   np.load(FEATURES), load_npz(INTERACTIONS))

    def scores(self, seed, mode, diversity=0.5):
        if seed is None or mode == "Popular":
            return minmax_scale(self.popularity.astype(float)), "Popularity"
        content = np.einsum("ij,j->i", self.audio_unit, self.audio_unit[seed])
        if mode == "Content":
            return minmax_scale(content), "Audio similarity"
        if not self.popularity[seed]:
            return minmax_scale(content), "Audio similarity (cold start)"
        collaborative = (self.interaction_unit @ self.interaction_unit[seed].T).toarray().ravel()
        if mode == "Collaborative":
            return collaborative, "Shared listeners"
        return ((1 - diversity) * minmax_scale(content) + diversity * collaborative,
                "Audio similarity and shared listeners")

    def recommend(self, track_id, mode, k=10, diversity=0.5, genre="", mood="", hidden=()):
        seed = self.indices[track_id] if track_id is not None else None
        scores, reason = self.scores(seed, mode, diversity)
        eligible = ~self.catalog.track_id.isin(hidden).to_numpy()
        if genre:
            eligible &= self.catalog.genre.eq(genre).to_numpy()
        if mood:
            eligible &= self.catalog.mood.eq(mood).to_numpy()
        if seed is not None:
            eligible[seed] = False
            if reason == "Shared listeners":
                eligible &= scores > 0
        ranked = np.lexsort((np.arange(len(scores)), -self.popularity, -scores))
        selected = ranked[eligible[ranked]][:k]
        result = self.catalog.iloc[selected].copy()
        result["score"] = scores[selected]
        result["listeners"] = self.popularity[selected]
        result["reason"] = reason
        return result
