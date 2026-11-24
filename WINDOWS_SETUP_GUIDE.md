# Windows setup guide

## On this laptop

1. Project folder kholo aur **start.bat** pe double-click karo.
2. Browser me app khul jayega. URL http://127.0.0.1:8000 hai.
3. App band karne ke liye **stop.bat** pe double-click karo.

Fresh copy ke liye Python 3.12 aur Git install hone ke baad **setup.bat** ek baar chalao. Setup ko internet chahiye. Data aur models ban jaane ke baad local app offline start ho sakti hai. Audio previews ko internet chahiye.

## Docker

Once Docker Desktop and WSL 2 are working, run **setup.bat** once and then **start_docker.bat**. Compose uses the prepared data read-only and saves favorites in a named volume. **stop_docker.bat** stops the Compose project. Its configured local address is http://127.0.0.1:8001.
