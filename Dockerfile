FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements-app.txt .
RUN python -m pip install --no-cache-dir -r requirements-app.txt \
    && useradd --create-home --uid 10001 app \
    && mkdir -p /app/.runtime /app/data/local /app/reports \
    && chown app:app /app/.runtime
COPY app.py LICENSE ./
COPY src/ src/
COPY .streamlit/ .streamlit/
USER app
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/_stcore/health', timeout=3)"
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8000", "--server.headless=true"]
