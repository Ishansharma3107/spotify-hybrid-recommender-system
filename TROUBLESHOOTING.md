# Troubleshooting

- **App opens with a missing-data error.** Run **setup.bat** and wait for it to finish.
- **Port 8000 is busy.** **stop.bat** stops the project server when it owns the port. If another application owns it, close that application or use an alternate Streamlit port.
- **Setup cannot download data.** Download the two named CSVs from the linked Kaggle dataset into `data/raw` and rerun setup. The upstream S3 remote requires authorized access.
- **Launch fails.** Open `.runtime/streamlit-error.log` in the project folder.
- **Preview has no audio.** Availability depends on the dataset URL and Spotify's preview service.
- **Docker cannot connect.** Open Docker Desktop and wait for the engine. If Windows asks for a restart, save your work and restart first.
