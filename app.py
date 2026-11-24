import json
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from src.recommender import AUDIO, METRICS, ROOT, Recommender

TITLE = "Spotify Hybrid Recommender System"
PAGES = {
    "Home": None, "Content-Based Recommendations": "Content",
    "Collaborative Recommendations": "Collaborative", "Hybrid Recommendations": "Hybrid",
    "Music Discovery": "Popular", "Data Analytics": None, "Model Performance": None,
    "About Project": None,
}


@st.cache_resource
def load_model():
    return Recommender.load()


def feedback(track_id=None, value=None):
    directory = ROOT / ".runtime"
    directory.mkdir(exist_ok=True)
    with sqlite3.connect(directory / "feedback.db") as db:
        db.execute("CREATE TABLE IF NOT EXISTS feedback (track_id TEXT PRIMARY KEY, value TEXT)")
        if value is not None:
            if value == "clear":
                db.execute("DELETE FROM feedback WHERE track_id = ?", (track_id,))
            else:
                db.execute("INSERT OR REPLACE INTO feedback VALUES (?, ?)", (track_id, value))
        return dict(db.execute("SELECT track_id, value FROM feedback"))


def cards(results, saved):
    if results.empty:
        st.info("No matches. Try clearing a filter or selecting another track.")
    for item in results.itertuples():
        with st.container(border=True):
            st.subheader(item.name)
            st.caption(f"{item.artist} · {item.genre} · {item.mood}")
            st.write(f"{item.reason} · score {item.score:.3f} · {item.listeners:,} sampled listeners")
            if isinstance(item.spotify_preview_url, str) and item.spotify_preview_url.startswith("https://p.scdn.co/"):
                st.audio(item.spotify_preview_url)
            first, second = st.columns(2)
            liked = saved.get(item.track_id) == "favorite"
            first.button("Remove favorite" if liked else "Favorite", key=f"fav-{item.track_id}",
                         on_click=feedback, args=(item.track_id, "clear" if liked else "favorite"))
            second.button("Hide", key=f"hide-{item.track_id}",
                          on_click=feedback, args=(item.track_id, "hidden"))


def recommendations(model, mode):
    tracks = model.catalog
    a, b, c = st.columns(3)
    genre = a.selectbox("Genre", ["", *sorted(tracks.genre.unique())], format_func=lambda v: v or "All genres")
    mood = b.selectbox("Mood", ["", *sorted(tracks.mood.unique())], format_func=lambda v: v or "All moods")
    k = c.slider("Results", 5, 20, 10)
    saved = feedback()
    hidden = [key for key, value in saved.items() if value == "hidden"]
    seed = None
    if mode == "Popular":
        view = st.radio("Discovery view", ["Popular tracks", "Favorites", "Hidden tracks"], horizontal=True)
        if view != "Popular tracks":
            kind = "favorite" if view == "Favorites" else "hidden"
            selected = tracks[tracks.track_id.map(saved).eq(kind)]
            if selected.empty:
                st.info(f"No {view.lower()} yet.")
            for item in selected.itertuples():
                st.button(f"Remove {item.name} by {item.artist} from {view.lower()}",
                          key=f"clear-{item.track_id}", on_click=feedback, args=(item.track_id, "clear"))
            return
    else:
        query = st.text_input("Search by track or artist").strip()
        if query:
            valid = tracks.name.str.contains(query, case=False, regex=False) | tracks.artist.str.contains(
                query, case=False, regex=False)
            candidates = tracks[valid].head(200)
        else:
            candidates = tracks.iloc[model.popularity.argsort()[::-1][:100]]
        if candidates.empty:
            st.info("No matching tracks or artists.")
            return
        labels = {row.track_id: f"{row.name} — {row.artist} ({row.track_id})" for row in candidates.itertuples()}
        seed = st.selectbox("Seed track", list(labels), format_func=labels.__getitem__)
    diversity = 0.5
    if mode == "Hybrid":
        diversity = st.slider("Diversity (collaborative weight)", 0.0, 1.0, 0.5, 0.1)
    with st.spinner("Ranking tracks…"):
        cards(model.recommend(seed, mode, k, diversity, genre, mood, hidden), saved)


def analytics(model):
    tracks = model.catalog
    a, b, c = st.columns(3)
    a.metric("Tracks", f"{len(tracks):,}")
    b.metric("Sampled listeners", f"{model.interactions.shape[1]:,}")
    c.metric("Unique listener–track pairs", f"{model.interactions.nnz:,}")
    genre = tracks.genre.value_counts().head(15).rename_axis("genre").reset_index(name="tracks")
    st.plotly_chart(px.bar(genre, x="genre", y="tracks", title="Largest genres"))
    feature = st.selectbox("Audio feature", AUDIO)
    st.plotly_chart(px.histogram(tracks, x=feature, title="Audio feature distribution"))
    st.plotly_chart(px.imshow(tracks[AUDIO].corr(), color_continuous_scale="RdBu_r",
                             zmin=-1, zmax=1, title="Audio feature correlations"))
    st.plotly_chart(px.histogram(x=model.popularity, log_y=True, labels={"x": "Sampled listeners"},
                                title="Track popularity"))


def performance():
    if not METRICS.is_file():
        st.info("Run the local pipeline to generate evaluation metrics.")
        return
    result = json.loads(METRICS.read_text(encoding="utf-8"))
    st.caption(f'{result["test_profiles"]:,} held-out listener profiles · one target per profile')
    scores = pd.DataFrame(result["models"]).T.rename_axis("Model")
    st.dataframe(scores.style.format("{:.4f}"))
    st.plotly_chart(px.bar(scores, barmode="group", title="Ranking performance at 10"))
    st.write("Item similarities use training listeners only. Results describe this offline sample.")


def main():
    st.set_page_config(page_title=TITLE, page_icon="🎵", layout="wide")
    page = st.sidebar.radio("Navigation", list(PAGES))
    st.title(TITLE if page == "Home" else page)
    if page == "About Project":
        st.write("Explore music recommendations based on audio features, shared listening patterns, or a blend of both.")
        st.write("The demo uses a sample of Spotify and Last.fm listening data and runs locally on Windows.")
        return
    if page == "Model Performance":
        performance()
        return
    try:
        with st.spinner("Loading the local catalog…"):
            model = load_model()
    except (OSError, ValueError) as error:
        st.error(f"Could not load local data. Run setup.bat to rebuild it. Details: {error}")
        return
    if page == "Home":
        st.write("Find similar tracks by sound, by shared listeners, or by combining both.")
        st.metric("Tracks available", f"{len(model.catalog):,}")
        st.markdown("Use the sidebar to choose a recommendation model or explore the dataset.")
    elif page == "Data Analytics":
        analytics(model)
    else:
        recommendations(model, PAGES[page])


if __name__ == "__main__":
    main()
