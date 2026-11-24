# Spotify Hybrid Recommender System

## Abstract

Music catalogs require ranking methods that can use both track attributes and listener behavior. This project implements a Windows-friendly music discovery application with audio and collaborative cosine similarity, a tunable hybrid model, and a popularity baseline. Sparse interaction storage and deterministic listener sampling enable local operation. An offline evaluation compares ranking methods on unseen listeners.

## Problem statement and objectives

A user starts with a song or a genre and needs a short, relevant list of tracks. User history is incomplete for many tracks. The objectives are to offer track search, compare three similarity-based recommenders, handle missing history, provide explainable results, and reproduce the data processing and evaluation locally.

## Literature review outline

- Recommender foundations and the cold-start problem. See the [recommender systems survey by Adomavicius and Tuzhilin](https://doi.org/10.1109/TKDE.2005.99).
- Item-based collaborative filtering. Compare item similarity, feedback types and sparsity. See [Sarwar et al.](https://doi.org/10.1145/371920.372071).
- Hybrid recommenders and weighted combination. See [Burke's survey](https://doi.org/10.1023/A:1021240730564).
- Music datasets and evaluation. Discuss [the Million Song Dataset Challenge](https://www.kaggle.com/competitions/msdchallenge), sampled listen histories and ranking metrics.

## Proposed methodology and algorithms

1. Obtain the two public CSVs and verify their checksums against the upstream dataset pointers.
2. Remove duplicate track IDs and invalid identifiers, impute missing audio features with their medians, and aggregate duplicate listener–track records.
3. Sample listener histories deterministically and join them to the track catalog by ID.
4. Scale numeric audio features and build a sparse track-by-listener matrix with log-transformed play counts.
5. Rank candidates with audio cosine, listening cosine, their weighted sum, or distinct-listener popularity. Apply filters and exclude the selected track.
6. Partition listeners into train and test. Evaluate a fixed, randomly selected seed–target pair per eligible test profile at rank ten.

## Architecture and data flow

See [architecture and data flow](../PROJECT_ARCHITECTURE.md). The stack uses Python, pandas, NumPy, SciPy, scikit-learn, Streamlit, Plotly, SQLite, DVC, Jupyter, pytest, Docker Compose and GitHub Actions.

## Results and testing

The evaluation used 3,368 held-out listener profiles.

| Model | Recall@10 | MRR@10 | NDCG@10 |
| --- | ---: | ---: | ---: |
| Popular | 6.53% | 0.0305 | 0.0386 |
| Content | 0.06% | 0.0001 | 0.0002 |
| Collaborative | 8.67% | 0.0443 | 0.0543 |
| Hybrid | 8.58% | 0.0434 | 0.0534 |

Collaborative filtering ranked first on this split. Hybrid with the default 50/50 blend was close behind. Audio-only filtering rarely retrieved the single exact held-out track in this catalog.

The computed result is stored in [model_metrics.json](model_metrics.json) and the executed output in [Local Analysis](../notebooks/Local_Analysis.ipynb). The testing and verification status for this laptop is in [PROGRESS.md](../PROGRESS.md).

| Verification | Result |
| --- | --- |
| Python dependencies and environment | pip check and environment check passed |
| Recommendation and data tests | 4 passed with real artifacts present |
| Windows startup and browser | Setup, start and stop verified. Live search, hybrid controls, analytics and performance pages verified |
| DVC | All four stages ran. Re-run up to date. Six objects in sync with local remote |
| Notebooks | Three upstream notebooks and the new analysis executed |
| Docker and cloud | Static configuration checks passed. Docker runtime and AWS rollout remain unverified |

## Limitations

The sample may miss useful co-listening signals for infrequently played tracks. Mood tags are feature-based heuristics. The offline protocol measures whether a known positive track can be rediscovered, and one target per profile produces a narrow measurement. Results depend on this catalog and sample. Preview availability depends on Spotify's URLs.

## Future scope

Evaluate temporal splits when timestamps are available, compare matrix factorization, tune blend weights on a separate validation split, and measure artist coverage and popularity bias alongside ranking quality.

## Conclusion

The system provides data-driven track ranking and applies explicit fallbacks when listening history is absent. The local workflow lets a reviewer regenerate the features, interaction matrix, and evaluation from the published source files.

## Attribution

See [credits and data provenance](../ATTRIBUTION.md) for original implementation and dataset acknowledgments.

## Presentation outline

1. Title, authorship and attribution
2. Motivation and problem statement
3. Dataset provenance and sampling
4. Architecture and data flow
5. Content and collaborative similarity
6. Hybrid blend, cold start and discovery
7. Streamlit demonstration
8. Held-out evaluation and measured comparison
9. Testing, DVC and deployment options
10. Limitations, future scope and questions

See [viva questions and answers](../VIVA_QUESTIONS.md).
