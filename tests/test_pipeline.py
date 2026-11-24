"""Exercise the full pipeline on a small deterministic fixture."""
import json

import numpy as np
import pandas as pd

from src import local_pipeline as pipeline
from src.recommender import AUDIO, Recommender


def test_preprocessing_training_and_evaluation(tmp_path, monkeypatch):
    raw = tmp_path / "raw"
    raw.mkdir()
    tracks = pd.DataFrame({
        "track_id": ["a", "a", "b", "c", None],
        "name": ["One", "Duplicate", "Two", "Three", "Invalid"],
        "artist": ["A", "A", "B", "C", "C"],
        "genre": ["Rock", "Rock", "Jazz", None, None],
        "spotify_preview_url": [""] * 5,
        **{feature: [0.2, 0.1, 0.7, np.nan, 0.9] for feature in AUDIO},
    })
    tracks.to_csv(raw / pipeline.MUSIC, index=False)
    candidates = pd.Series([f"user-{i}" for i in range(1000)])
    sampled = candidates[pd.util.hash_pandas_object(candidates, index=False) % 50 == 0].head(8)
    rows = [(user, track, 1) for user in sampled for track in ["a", "a", "b", "c", "unknown"]]
    pd.DataFrame(rows, columns=["user_id", "track_id", "playcount"]).to_csv(raw / pipeline.HISTORY, index=False)
    monkeypatch.setattr(pipeline, "RAW", raw)
    for attr, filename in {
        "CATALOG": "catalog.csv", "LOCAL_HISTORY": "listens.csv",
        "FEATURES": "audio.npy", "INTERACTIONS": "interactions.npz", "METRICS": "metrics.json",
    }.items():
        monkeypatch.setattr(pipeline, attr, tmp_path / filename)
    pipeline.preprocess()
    pipeline.features()
    pipeline.train()
    pipeline.evaluate()
    from scipy.sparse import load_npz

    catalog = pd.read_csv(pipeline.CATALOG)
    model = Recommender(catalog, np.load(pipeline.FEATURES), load_npz(pipeline.INTERACTIONS))
    assert catalog.track_id.tolist() == ["a", "b", "c"]
    assert catalog.genre.tolist() == ["Rock", "Jazz", "Unknown"]
    assert model.interactions.shape == (3, 8)
    np.testing.assert_allclose(model.interactions[0].data, np.log1p(2))
    assert model.recommend("a", "Hybrid").track_id.isin(["b", "c"]).all()
    metrics = json.loads(pipeline.METRICS.read_text(encoding="utf-8"))
    assert metrics["test_profiles"] == 1
    assert set(metrics["models"]) == {"Popular", "Content", "Collaborative", "Hybrid"}
