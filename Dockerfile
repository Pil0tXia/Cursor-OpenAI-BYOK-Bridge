FROM python:3.11-slim

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    HOST=0.0.0.0 \
    PORT=7860 \
    DASHBOARD_ENABLED=true \
    DASHBOARD_TITLE="BYOK Relay Logs" \
    LOG_DB=/tmp/byok-requests.sqlite3

WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

CMD ["python", "run.py"]
