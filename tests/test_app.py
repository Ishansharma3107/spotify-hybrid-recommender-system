from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy.sparse import csr_matrix
from streamlit.testing.v1 import AppTest

import src.recommender as engine

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def model():
    catalog = pd.DataFrame({
        "track_id": ["a", "b", "c", "d"],
        "name": ["First", "Soundalike", "Shared", "New"],
        "artist": ["Alice", "Bob", "Carol", "Dan"],
        "genre": ["Rock", "Rock", "Pop", "Pop"],
        "mood": ["Calm", "Calm", "Upbeat", "Upbeat"],
        "spotify_preview_url": [""] * 4,
    })
    for column in engine.AUDIO:
        catalog[column] = [0.1, 0.2, 0.3, 0.4]
    return engine.Recommender(catalog, np.array([[1, 0], [.95, .05], [0, 1], [.6, .6]]),
                              csr_matrix([[1, 1], [0, 1], [1, 1], [0, 0]]))


def test_recommendations(model):
    assert model.recommend("a", "Content").track_id.iloc[0] == "b"
    assert model.recommend("a", "Collaborative").track_id.tolist() == ["c", "b"]
    assert model.recommend("a", "Hybrid", diversity=0).track_id.iloc[0] == "b"
    assert model.recommend("a", "Hybrid", diversity=1).track_id.iloc[0] == "c"
    assert model.recommend("d", "Collaborative").reason.str.contains("cold start").all()
    assert model.recommend(None, "Popular", genre="Pop", mood="Upbeat", hidden=["c"]).track_id.tolist() == ["d"]
    assert model.recommend("a", "Content", genre="Rock").track_id.tolist() == ["b"]


def test_app_loading_and_controls(model, monkeypatch, tmp_path):
    monkeypatch.setattr(engine, "ROOT", tmp_path)
    monkeypatch.setattr(engine.Recommender, "load", classmethod(lambda cls: model))
    metrics = tmp_path / "metrics.json"
    metrics.write_text('{"test_profiles":1,"models":{"Content":{"Recall@10":1}}}', encoding="utf-8")
    monkeypatch.setattr(engine, "METRICS", metrics)
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    assert app.title[0].value == "Spotify Hybrid Recommender System"
    for page in app.sidebar.radio[0].options:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception, page
    app.sidebar.radio[0].set_value("Hybrid Recommendations").run()
    app.text_input[0].set_value("Alice").run()
    assert app.selectbox[2].value == "a"
    app.slider[1].set_value(1.0).run()
    assert not app.exception
    assert app.subheader[0].value == "Shared"
    app.button[0].click().run()
    assert app.button[0].label == "Remove favorite"
    app.button[1].click().run()
    assert all(item.value != "Shared" for item in app.subheader)
    app.text_input[0].set_value("missing artist").run()
    assert app.info[0].value == "No matching tracks or artists."


def test_real_artifacts_if_available():
    if not engine.INTERACTIONS.is_file():
        pytest.skip("Local dataset has not been built")
    import json

    model = engine.Recommender.load()
    assert model.catalog.track_id.is_unique
    assert model.interactions.nnz > 0
    assert np.isfinite(model.audio).all()
    seed = model.catalog.iloc[model.popularity.argmax()].track_id
    for mode in ("Content", "Collaborative", "Hybrid", "Popular"):
        ranked = model.recommend(seed, mode)
        assert len(ranked) == 10
        assert seed not in ranked.track_id.values
    metrics = json.loads(engine.METRICS.read_text(encoding="utf-8"))
    assert metrics["test_profiles"] > 0
    assert all(0 <= value <= 1 for scores in metrics["models"].values() for value in scores.values())
