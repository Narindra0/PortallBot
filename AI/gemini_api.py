import re

from google import genai

from AI.openrouter_api import (
    generer_lettre_motivation_openrouter_async,
    generer_resume_entreprise_openrouter_async,
)
from AI.prompt_cover_letter import SYSTEM_PROMPT, build_user_prompt
from Bot.config import GEMINI_API_KEY, OPENROUTER_API_KEY
from Bot.utils.logger import logger

# Configuration du modèle pour 2026
MODEL_NAME = "gemini-2.0-flash"


def nettoyer_reponse_ai(text):
    """
    Nettoie les réponses de l'IA pour Telegram (HTML).
    """
    if not text:
        return ""

    # 1. Supprimer les blocs <think> complets (Insensible à la casse)
    text = re.sub(r"<(think)>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Supprimer un début de <think> orphelin
    text = re.sub(r"<(think)>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)

    # 3. Supprimer tout tag HTML non supporté par Telegram (b, i, a, code, pre)
    text = re.sub(r"<(?!/?(b|i|a|code|pre)\b)[^>]+>", "", text, flags=re.IGNORECASE)

    # 4. Nettoyage résiduel
    text = text.replace("**", "").replace("---", "").strip()

    return text


async def generer_lettre_motivation_gemini_async(cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details):
    """Génère une lettre de motivation via Google Gemini 2.0 Flash, avec fallback OpenRouter."""
    # Essayer Gemini d'abord
    if GEMINI_API_KEY:
        try:
            # Nouveau client 2026
            client = genai.Client(api_key=GEMINI_API_KEY)

            # Construire le prompt complet
            prompt = (
                SYSTEM_PROMPT
                + "\n\n"
                + build_user_prompt(
                    cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details
                )
            )

            # Appel asynchrone via .aio (nouveauté 2026)
            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response and response.text:
                return nettoyer_reponse_ai(response.text)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ Gemini quota épuisé pour {offre_titre}, fallback OpenRouter...")
            else:
                logger.error(f"Erreur Gemini 2.0 (Lettre): {e}")

    # Fallback sur OpenRouter
    if OPENROUTER_API_KEY:
        logger.info(f"🔄 Fallback OpenRouter pour lettre: {offre_titre}")
        return await generer_lettre_motivation_openrouter_async(cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details)

    return None


async def generer_resume_entreprise_gemini_async(nom_entreprise, contexte=""):
    """Génère un résumé d'entreprise via Google Gemini 2.0, avec fallback OpenRouter."""
    # Essayer Gemini d'abord
    if GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)

            prompt = (
                f"Résume en une phrase l'activité de l'entreprise '{nom_entreprise}'.\n"
                f"Contexte: {contexte}\n"
                f"RÈGLE: Une seule phrase, directe, sans introduction, sans markdown."
            )

            response = await client.aio.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            if response and response.text:
                return nettoyer_reponse_ai(response.text)

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ Gemini quota épuisé pour {nom_entreprise}, fallback OpenRouter...")
            else:
                logger.error(f"Erreur Gemini 2.0 (Résumé): {e}")

    # Fallback sur OpenRouter
    if OPENROUTER_API_KEY:
        logger.info(f"🔄 Fallback OpenRouter pour résumé entreprise: {nom_entreprise}")
        return await generer_resume_entreprise_openrouter_async(nom_entreprise, contexte)

    return None
