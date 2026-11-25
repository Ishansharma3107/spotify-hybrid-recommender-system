# Spotify Hybrid Recommender System

Ishan Sharma

Explore music using audio similarity, shared listening patterns, or a tunable blend of both. The Streamlit app runs on Windows with local data and model file

- Built eight Streamlit sections for recommendations, discovery, analytics, and model comparison.
- Added track and artist search, genre and mood filters, popularity ranking, cold-start fallback, and recommendation explanations.
- Added favorites and hidden-track feedback in SQLite and aligned recommendations by track ID.
- Added checksum-verified data downloads, chunked listener sampling, sparse artifacts, and a reproducible local DVC pipeline.
- Added a VS Code run task, Windows startup scripts, automated tests, and an executed analysis notebook.
- Prepared Docker Compose and optional AWS deployment.

## Run on Windows

1. Install Python 3.12 and run `setup.bat` once to install dependencies and build the local artifacts.
2. Open the project folder in VS Code, press **Ctrl+Shift+B**, then open [http://127.0.0.1:8501](http://127.0.0.1:8501).

The app and recommendations work offline after setup. Audio previews may need internet.

## Evaluation

The sample contains 50,683 tracks and 191,805 unique listener–track pairs. On 3,368 held-out profiles, Recall@10 was 8.67% for collaborative filtering, 8.58% for hybrid, 6.53% for popularity, and 0.06% for audio-only filtering. See the [evaluation metrics](reports/model_metrics.json) and [executed analysis notebook](notebooks/Local_Analysis.ipynb).
