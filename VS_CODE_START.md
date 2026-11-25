# Run manually on Windows

Open the project folder in VS Code and select **Terminal → New Terminal**. Use PowerShell from the project root. If this is a fresh checkout, complete the setup below first.

```powershell
& '.\.venv\Scripts\python.exe' -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501) in your browser. Press **Ctrl+C** in the terminal to stop Streamlit. Stop any previous run on port 8501 before starting another. The same command works in standalone PowerShell. The command uses the local Python environment and generated data.

## Run from the VS Code task

Press **Ctrl+Shift+B** to start **Start Spotify Recommender**. VS Code runs the same Python module and shows its output in the Terminal panel. For editor features, select `.venv\Scripts\python.exe` using **Python: Select Interpreter** if VS Code has remembered a different interpreter.

## Set up a fresh copy

Install Python 3.12 and Git. Open PowerShell in the project folder and run:

```powershell
.\setup.bat
```

Setup creates `.venv` if needed, installs the pinned requirements, and builds the local data artifacts with DVC. It needs internet access for packages and any missing raw data. If the dataset download fails, see [Troubleshooting](TROUBLESHOOTING.md). Once set up, recommendations work offline. Audio preview availability depends on the internet and the preview URL.

If you already have the prepared data on another Windows machine, copy `data/local/catalog.csv`, `data/local/audio.npy`, and `data/local/interactions.npz` into the same paths. Copy `reports/model_metrics.json` for evaluation results. To install just the app dependencies in a fresh environment, run:

```powershell
py -3.12 -m venv .venv
& '.\.venv\Scripts\python.exe' -m pip install -r requirements-app.txt
& '.\.venv\Scripts\python.exe' -m pip check
```

After full setup, run the tests with `& '.\.venv\Scripts\python.exe' -m pytest -q`.
