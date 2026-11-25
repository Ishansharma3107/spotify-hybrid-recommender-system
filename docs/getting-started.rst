Getting started
===============

Install Python 3.12 and Git. From the project root on Windows, run
``setup.bat`` to create the local environment, install dependencies, and
prepare the recommender data. Then run ``start.bat`` and open
``http://127.0.0.1:8000``.

For a terminal launch from the project root, run this in PowerShell::

    & '.\.venv\Scripts\python.exe' -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501

Open ``http://127.0.0.1:8501`` and press Ctrl+C in the terminal to stop
the app. Setup downloads the raw dataset from Kaggle when necessary.
The local app uses the generated files in ``data/local``.
