#!/usr/bin/env python3
"""
Module pour l'API Groq (très rapide !)
"""
import re
import asyncio
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

async def generer_lettre_motivation_groq_async(cv_text, offre_titre, offre_entreprise, offre_details, portfolio=""):
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

        context_portfolio = f"Voici mon portfolio pour appuyer ma candidature : {portfolio}" if portfolio else ""

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un expert en recrutement rédigeant des lettres de motivation percutantes, professionnelles et authentiques.\n"
                    "\nRÈGLES STRICTES :\n"
                    "1. Produis une lettre de motivation de bonne qualité, concise et percutante (pas trop longue pour ne pas lasser les recruteurs), avec une structure claire et des arguments ciblés sur le poste visé.\n"
                    "2. S'appuie EXCLUSIVEMENT sur les informations contenues dans le CV fourni. Ne jamais ajouter d'expérience, compétence ou réalisation non mentionnée dans le CV.\n"
                    "3. Vérifie systématiquement que TOUTES les informations dans la lettre correspondent EXACTEMENT à des éléments présents dans le CV fourni. Aucune information inventée !\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Rédige une lettre de motivation unique et humaine pour le poste suivant.\n\n"
                    f"POSTE : {offre_titre}\n"
                    f"ENTREPRISE : {offre_entreprise}\n"
                    f"DÉTAILS OFFRE : {offre_details}\n\n"
                    f"MON CV :\n{cv_text}\n\n"
                    f"{context_portfolio}\n\n"
                    f"AUTRES RÈGLES :\n"
                    "- Texte brut uniquement. Pas de markdown (pas de **, pas de #, pas de ```).\n"
                    "- Pas d'en-tête (adresse, date, objet).\n"
                    "- Pas d'introduction type 'Voici votre lettre' ou 'Voici la lettre'.\n"
                    "- Commence directement par 'Madame, Monsieur,' ou le nom du recruteur si connu.\n"
                    "- Ton professionnel mais chaleureux et authentique.\n"
                    "- Maximum 2500 caractères."
                )
            }
        ]

        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )

        raw_text = response.choices[0].message.content
        clean_text = nettoyer_reponse_ai(raw_text)
        logger.info("✅ Lettre générée avec Groq !")
        return clean_text

    except Exception as e:
        logger.error(f"❌ Erreur avec Groq: {e}")
        return None
