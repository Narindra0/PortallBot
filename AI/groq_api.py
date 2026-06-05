#!/usr/bin/env python3
"""
Module pour l'API Groq (très rapide !)
"""
import re

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

        # Build user info string
        user_info_parts = [f"Nom : {cv_user['nom']}", f"Email : {cv_user['email']}"]
        if cv_user.get('telephone'):
            user_info_parts.append(f"Téléphone : {cv_user['telephone']}")
        if cv_user.get('portfolio'):
            user_info_parts.append(f"Portfolio : {cv_user['portfolio']}")

        # Build CV parsed info string
        cv_parsed_parts = []
        if cv_parsed.get('competences'):
            cv_parsed_parts.append(f"Compétences clés : {', '.join(cv_parsed['competences'])}")
        if cv_parsed.get('annees_exp'):
            cv_parsed_parts.append(f"Années d'expérience : {cv_parsed['annees_exp']}")
        if cv_parsed.get('postes'):
            cv_parsed_parts.append(f"Postes précédents : {', '.join(cv_parsed['postes'])}")
        if cv_parsed.get('niveau_etudes'):
            cv_parsed_parts.append(f"Niveau d'études : {cv_parsed['niveau_etudes']}")
        if cv_parsed.get('extrait_important'):
            cv_parsed_parts.append(f"Extrait important : {cv_parsed['extrait_important']}")

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un expert en recrutement rédigeant des lettres de motivation percutantes, professionnelles et authentiques.\n"
                    "\nRÈGLES STRICTES :\n"
                    "1. Produis une lettre de motivation concise (maximum 2000 caractères), percutante et adaptée au poste visé.\n"
                    "2. S'appuie EXCLUSIVEMENT sur les informations fournies (informations personnelles, CV, parsed CV). Ne jamais ajouter d'expérience, compétence ou réalisation non mentionnée.\n"
                    "3. Vérifie systématiquement que TOUTES les informations dans la lettre correspondent EXACTEMENT à des éléments fournis. Aucune information inventée !\n"
                    "4. Intègre de manière naturelle les informations de contact (email, téléphone si disponible) et portfolio si disponible.\n"
                    "5. Mentionne explicitement les compétences et expériences pertinentes du CV qui correspondent aux exigences du poste.\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Rédige une lettre de motivation unique et humaine pour le poste suivant.\n\n"
                    f"POSTE : {offre_titre}\n"
                    f"ENTREPRISE : {offre_entreprise}\n"
                    f"DÉTAILS OFFRE : {offre_details}\n\n"
                    f"MES INFORMATIONS PERSONNELLES :\n{chr(10).join(user_info_parts)}\n\n"
                    f"MON CV COMPLET :\n{cv_user['cv_text']}\n\n"
                    f"MON CV ANALYSÉ :\n{chr(10).join(cv_parsed_parts)}\n\n"
                    f"AUTRES RÈGLES :\n"
                    "- Texte brut uniquement. Pas de markdown.\n"
                    "- Pas d'en-tête (adresse, date, objet).\n"
                    "- Commence directement par 'Madame, Monsieur,'.\n"
                    "- Ton professionnel mais chaleureux et authentique."
                )
            }
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
