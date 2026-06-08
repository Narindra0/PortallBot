#!/usr/bin/env python3
"""
Module pour l'API Groq (très rapide !)
"""
import re

from AI.prompt_cover_letter import SYSTEM_PROMPT, build_user_prompt
from Bot.config import GROQ_API_KEY
from Bot.utils.logger import logger

# Import de la fonction de nettoyage depuis openrouter_api.py
try:
    from AI.openrouter_api import nettoyer_reponse_ai
except ImportError:
    def nettoyer_reponse_ai(text):
        if not text:
            return ""
        text = re.sub(r"<(think|thinking)>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<(?!/?(b|i|a|code|pre)\b)[^>]+>", "", text, flags=re.IGNORECASE)
        text = text.replace("**", "").replace("*", "").replace("---", "").replace("```", "").strip()
        return text

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ Bibliothèque groq non installée. Installer avec 'pip install groq'")
    GROQ_AVAILABLE = False

# Modèle Groq par défaut (très rapide !)
GROQ_MODEL = "llama-3.1-8b-instant"

# Client Groq (initialisation paresseuse)
_client = None


def get_groq_client():
    """
    Retourne le client Groq asynchrone (singleton)
    """
    global _client
    if not GROQ_AVAILABLE:
        raise ImportError("Bibliothèque groq non installée")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY non configuré dans .env")

    if _client is None:
        _client = AsyncGroq(api_key=GROQ_API_KEY)
    return _client


async def generer_lettre_motivation_groq_async(cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details):
    """
    Génère une lettre de motivation via l'API Groq.
    """
    if not GROQ_AVAILABLE:
        logger.error("Bibliothèque groq non installée")
        return None
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY manquante")
        return None

    try:
        client = get_groq_client()
        logger.info(f"🔄 Tentative avec Groq (modèle: {GROQ_MODEL})...")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_user_prompt(
                    cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details
                ),
            },
        ]

        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=700
        )

        raw_text = response.choices[0].message.content
        clean_text = nettoyer_reponse_ai(raw_text)
        logger.info("✅ Lettre générée avec Groq !")
        return clean_text

    except Exception as e:
        logger.error(f"❌ Erreur avec Groq: {e}")
        return None
