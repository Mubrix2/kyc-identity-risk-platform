# Dockerfile
# FastAPI + consumer thread. Tesseract installed at OS level (pytesseract
# is just a wrapper). libgomp1 required by XGBoost's OpenMP backend.
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TESSERACT_CMD=/usr/bin/tesseract

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY data/sanctions/ ./data/sanctions/
COPY data/sample_ids/ ./data/sample_ids/

# Fail fast at build time if required artifacts are missing
RUN python3 - <<'PYEOF'
import sys
from pathlib import Path
required = [
    "app/models/risk_model.pkl",
    "data/sanctions/ofac_sdn.csv",
    "data/sanctions/illustrative_pep_list.csv",
]
missing = [m for m in required if not Path(m).exists()]
if missing:
    print("ERROR: Missing required files:")
    for m in missing:
        print(f"  {m}")
    sys.exit(1)
print(f"All {len(required)} required files verified.")
PYEOF

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]