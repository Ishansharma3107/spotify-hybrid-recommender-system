"""Create the reproducible EDA notebook source."""
from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
markdown = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell
nb.cells = [
    markdown("# Spotify Hybrid Recommender System\nAnalysis of the locally prepared Spotify / Last.fm sample."),
    code("""from pathlib import Path
import json
import sys

root = Path.cwd()
if not (root / 'src').exists():
    root = root.parent
sys.path.insert(0, str(root))
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from src.recommender import AUDIO, METRICS, Recommender

model = Recommender.load()
catalog = model.catalog
pd.Series({'tracks': len(catalog), 'listeners': model.interactions.shape[1],
           'unique listener-track pairs': model.interactions.nnz})
"""),
    code("""axes = catalog[AUDIO].hist(figsize=(11, 8), bins=30)
plt.suptitle('Audio feature distributions')
plt.tight_layout()
plt.show()"""),
    code("""catalog.genre.value_counts().head(15).sort_values().plot.barh(title='Tracks by genre')
plt.xlabel('Tracks')
plt.tight_layout()
plt.show()"""),
    code("""plt.figure(figsize=(9, 7))
sns.heatmap(catalog[AUDIO].corr(), cmap='vlag', vmin=-1, vmax=1, annot=True, fmt='.2f')
plt.title('Audio feature correlations')
plt.tight_layout()
plt.show()"""),
    code("""plt.hist(model.popularity, bins=50, log=True)
plt.title('Popularity based on distinct sampled listeners')
plt.xlabel('Listeners per track')
plt.ylabel('Tracks (log scale)')
plt.show()"""),
    code("""metrics = json.loads(METRICS.read_text(encoding='utf-8'))
scores = pd.DataFrame(metrics['models']).T
scores.plot.bar(rot=15, title='Ranking performance on held-out listeners')
plt.ylabel('Mean score at 10')
plt.tight_layout()
plt.show()
print(f"Held-out profiles: {metrics['test_profiles']}")
scores"""),
]
nbf.write(nb, Path(__file__).with_name("Local_Analysis.ipynb"))
