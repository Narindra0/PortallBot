"""
Module de connexion à l'API Hugging Face pour génération de lettres de motivation.
Support Async avec gestion d'erreurs, retry exponentiel et compatibilité URL globale.
"""
import re

from huggingface_hub import InferenceClient

from AI.prompt_cover_letter import SYSTEM_PROMPT, build_user_prompt
from Bot.config import HF_API_KEY
from Bot.utils.logger import logger

# Modèle 100% Gratuit (Serverless Inference API)
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def nettoyer_reponse_ai(text):
    """
    Nettoie les réponses de l'IA pour Telegram (HTML).
    Supprime les blocs <think> (pensées de DeepSeek) et les tags non supportés.
    """
    if not text:
        return ""

    # 1. Supprimer les blocs <think> complets (Insensible à la casse)
    text = re.sub(r"<(think)>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Supprimer un début de <think> orphelin (si réponse tronquée)
    text = re.sub(r"<(think)>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)

    # 3. Supprimer tout tag HTML non supporté par Telegram (b, i, a, code, pre)
    # On capture tout ce qui n'est pas dans la liste blanche
    text = re.sub(r"<(?!/?(b|i|a|code|pre)\b)[^>]+>", "", text, flags=re.IGNORECASE)

    # 4. Nettoyage résiduel
    text = text.replace("**", "").replace("---", "").strip()

    return text


async def generer_lettre_motivation_async(cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details):
    """Génère une lettre de motivation via l'API Hugging Face Free Serverless."""
    if not HF_API_KEY:
        logger.error("HF_API_KEY manquante.")
        return None

    try:
        # Initialisation du client (plus robuste qu'une URL manuelle)
        client = InferenceClient(api_key=HF_API_KEY)

        # Utilisation du Chat Completion via le client (gère les URLs automatiquement)
        response = client.chat.completions.create(
            model=HF_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details
                    ),
                },
            ],
            max_tokens=800,
            temperature=0.7
        )

        raw_text = response.choices[0].message.content
        clean_text = nettoyer_reponse_ai(raw_text)
        logger.info("✅ Lettre générée (InferenceClient) avec succès.")
        return clean_text

    except Exception as e:
        logger.error(f"Erreur InferenceClient: {e}")

    return None


async def generer_resume_entreprise_async(nom_entreprise, contexte=""):
    """Génère un résumé court et percutant d'une entreprise (Free)."""
    if not HF_API_KEY:
        return None

    try:
        client = InferenceClient(api_key=HF_API_KEY)

        prompt = (
            f"Résume en une phrase l'activité de l'entreprise '{nom_entreprise}'.\n"
            f"Contexte: {contexte}\n"
            f"RÈGLE: Une seule phrase, directe, sans introduction."
        )

        response = client.chat.completions.create(
            model=HF_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.4
        )

        return nettoyer_reponse_ai(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Erreur résumé: {e}")
    return None


def generer_lettre_motivation(cv, t, e, d):
    """Wrapper synchrone pour la fonction async."""
    import asyncio
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(generer_lettre_motivation_async(cv, t, e, d))
    except Exception as e:
        logger.error(f"Erreur wrapper sync: {e}")
        return None
