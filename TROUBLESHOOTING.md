# Troubleshooting

- **App opens with a missing-data error.** Run **setup.bat** and wait for it to finish.
- **Port 8000 is busy.** **stop.bat** stops the project server when it owns the port. If another application owns it, close that application or use an alternate Streamlit port.
- **Setup cannot download data.** Download the [Spotify and Last.fm dataset](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm), extract `Music Info.csv` and `User Listening History.csv` into `data/raw`, and rerun setup.
- **Port 8501 is busy.** Stop the existing Streamlit run with **Ctrl+C** in its terminal, or use a different port for the manual command.
- **Launch fails.** Check the VS Code terminal for the task or manual run. If you used `start.bat`, open `.runtime/streamlit-error.log`.
- **Preview has no audio.** Availability depends on the dataset URL and Spotify's preview service.
- **Docker cannot connect.** Open Docker Desktop and wait for the engine. If Windows asks for a restart, save your work and restart first.
