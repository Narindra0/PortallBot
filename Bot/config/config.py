"""
Configuration centralisée du projet PortalBot.
Charge les variables d'environnement depuis .env (à la racine du projet).
"""
import os
from dotenv import load_dotenv

# Déterminer le chemin de base du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Dossier logs
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Charger les variables d'environnement
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

# === Chemins des sessions ===
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
ASAKO_SESSION_PATH = os.path.join(CONFIG_DIR, 'asako_session.json')
PORTAL_SESSION_PATH = os.path.join(CONFIG_DIR, 'portal_session.json')

# === Telegram ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# === Hugging Face (Déprécié) ===
HF_API_KEY = os.getenv('HF_API_KEY')

# === Google Gemini (Fallback) ===
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# === OpenRouter (Gratuit - Prioritaire)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# === Groq (Très rapide - Optionnel)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# === Mode d'exécution ===
HEADLESS = os.getenv('HEADLESS', 'false').lower() == 'true'

# === Firecrawl (optionnel) ===
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')

# === Base de données ===
# Turso (SQLite cloud - optionnel, pour staging/production)
TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')

# Local SQLite (pour développement)
LOCAL_DB_PATH = os.getenv('LOCAL_DB_PATH', os.path.join(BASE_DIR, 'portalbot.db'))

# === SMTP Email Fallback ===
SMTP_EMAIL = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')  # Mot de passe d'application Gmail

# === CV PDF (stockage local temporaire) ===
CV_PDF_PATH = os.path.join(BASE_DIR, 'cv_utilisateur.pdf')


def verifier_configuration():
    """Vérifie que les variables essentielles sont configurées."""
    erreurs = []
    
    if not TELEGRAM_TOKEN:
        erreurs.append("TELEGRAM_TOKEN manquant")
    if not TELEGRAM_CHAT_ID or TELEGRAM_CHAT_ID == 'votre_chat_id_ici':
        erreurs.append("TELEGRAM_CHAT_ID non configuré")
    if not GEMINI_API_KEY:
        erreurs.append("GEMINI_API_KEY manquante (nécessaire pour les lettres de motivation et les résumés)")
    
    return erreurs


def est_configuration_valide():
    """Retourne True si la configuration minimale est présente."""
    return bool(TELEGRAM_TOKEN and TELEGRAM_CHAT_ID and TELEGRAM_CHAT_ID != 'votre_chat_id_ici')
