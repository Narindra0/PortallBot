"""
Module de génération de lettres de motivation.
Adapté pour l'asynchronisme.
Priorité: OpenRouter (gratuit) → Groq → Gemini → HuggingFace
"""
from Bot.storage.cache_db import (
    recuperer_cv_async,
    sauvegarder_lettre_motivation_async,
    recuperer_derniere_lettre_pour_offre_async,
    recuperer_lettres_pour_offre_async
)
from AI.openrouter_api import generer_lettre_motivation_openrouter_async
from AI.groq_api import generer_lettre_motivation_groq_async
from AI.gemini_api import generer_lettre_motivation_gemini_async
from AI.huggingface_api import generer_lettre_motivation_async as generer_lettre_motivation_hf_async
from Bot.config import OPENROUTER_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, HF_API_KEY
from Bot.utils.logger import logger


async def creer_lettre_motivation(offre_data, reuse_existing=True):
    """
    Crée une lettre de motivation personnalisée (Async).
    Essaye les APIs dans l'ordre: OpenRouter (gratuit) → Groq → Gemini → HuggingFace
    
    Args:
        offre_data: Dictionary containing job offer data
        reuse_existing: If True, try to reuse an existing letter for this job first
    """
    cv = await recuperer_cv_async()
    if not cv:
        return False, "❌ CV non configuré."

    titre = offre_data.get('titre', 'Poste non spécifié')
    entreprise = offre_data.get('entreprise', 'Entreprise non spécifiée')
    details = offre_data.get('details', '')
    portfolio = cv.get('portfolio', '')
    offre_url = offre_data.get('url', '')

    logger.info(f"📝 Préparation de la lettre pour: {titre} @ {entreprise}")

    # Check if we already have a letter for this job
    if reuse_existing and offre_url:
        existing_letter = await recuperer_derniere_lettre_pour_offre_async(offre_url)
        if existing_letter:
            logger.info("📄 Réutilisation de la lettre de motivation existante !")
            return True, existing_letter

    lettre = None

    # 1. Essayer OpenRouter (gratuit) - Prioritaire
    if OPENROUTER_API_KEY:
        logger.info("🔄 Tentative avec OpenRouter (gratuit)...")
        lettre = await generer_lettre_motivation_openrouter_async(
            cv['cv_text'], titre, entreprise, details, portfolio
        )
        if lettre:
            logger.info("✅ Lettre générée avec OpenRouter")
            if offre_url:
                await sauvegarder_lettre_motivation_async(offre_url, lettre)
            return True, lettre

    # 2. Fallback sur Groq (très rapide !)
    if GROQ_API_KEY:
        logger.info("🔄 Fallback sur Groq...")
        lettre = await generer_lettre_motivation_groq_async(
            cv['cv_text'], titre, entreprise, details, portfolio
        )
        if lettre:
            logger.info("✅ Lettre générée avec Groq")
            if offre_url:
                await sauvegarder_lettre_motivation_async(offre_url, lettre)
            return True, lettre

    # 3. Fallback sur Gemini
    if GEMINI_API_KEY:
        logger.info("🔄 Fallback sur Gemini...")
        lettre = await generer_lettre_motivation_gemini_async(
            cv['cv_text'], titre, entreprise, details, portfolio
        )
        if lettre:
            logger.info("✅ Lettre générée avec Gemini")
            if offre_url:
                await sauvegarder_lettre_motivation_async(offre_url, lettre)
            return True, lettre

    # 4. Dernier recours: HuggingFace
    if HF_API_KEY:
        logger.info("🔄 Dernier recours: HuggingFace...")
        lettre = await generer_lettre_motivation_hf_async(
            cv['cv_text'], titre, entreprise, details, portfolio
        )
        if lettre:
            logger.info("✅ Lettre générée avec HuggingFace")
            if offre_url:
                await sauvegarder_lettre_motivation_async(offre_url, lettre)
            return True, lettre

    return False, "❌ Échec de la génération (toutes les APIs sont indisponibles). Vérifiez vos clés API."

def formater_lettre_pour_telegram(lettre):
    """Découpe la lettre pour Telegram."""
    MAX_LENGTH = 3800
    if len(lettre) <= MAX_LENGTH:
        return [lettre]

    parts = []
    current = ""
    for line in lettre.split('\n'):
        if len(current) + len(line) + 1 > MAX_LENGTH:
            parts.append(current)
            current = line + '\n'
        else:
            current += line + '\n'
    if current:
        parts.append(current)
    return parts
