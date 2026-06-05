# Dockerfile pour PortalBot
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système pour Playwright et Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Installer le navigateur Playwright Chromium
RUN playwright install --with-deps chromium

# Copier tout le code
COPY . .

# Définir la variable d'environnement HEADLESS sur true (pour production)
ENV HEADLESS=true

# Exposer un port pour Back4App (même si non utilisé par le bot)
EXPOSE 8000

# Commande pour lancer le bot en mode complet
CMD ["python", "main.py", "all"]
