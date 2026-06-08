import re

from google import genai

from AI.openrouter_api import (
    generer_lettre_motivation_openrouter_async,
    generer_resume_entreprise_openrouter_async,
)
from Bot.config import GEMINI_API_KEY, OPENROUTER_API_KEY
from Bot.utils.logger import logger

# Configuration du modèle pour 2026
MODEL_NAME = "gemini-2.0-flash"

def nettoyer_reponse_ai(text):
    """
    Nettoie les réponses de l'IA pour Telegram (HTML).
    """
    if not text: return ""

    # 1. Supprimer les blocs <think> complets (Insensible à la casse)
    text = re.sub(r'<(think)>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 2. Supprimer un début de <think> orphelin
    text = re.sub(r'<(think)>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)

    # 3. Supprimer tout tag HTML non supporté par Telegram (b, i, a, code, pre)
    text = re.sub(r'<(?!/?(b|i|a|code|pre)\b)[^>]+>', '', text, flags=re.IGNORECASE)

    # 4. Nettoyage résiduel
    text = text.replace('**', '').replace('---', '').strip()

    return text

async def generer_lettre_motivation_gemini_async(cv_user, cv_parsed, offre_titre, offre_entreprise, offre_details):
    """Génère une lettre de motivation via Google Gemini 2.0 Flash, avec fallback OpenRouter."""
    # Essayer Gemini d'abord
    if GEMINI_API_KEY:
        try:
            # Nouveau client 2026
            client = genai.Client(api_key=GEMINI_API_KEY)

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

            prompt = (
                "Tu es un expert en recrutement rédigeant des lettres de motivation PERCUTANTES, SPÉCIFIQUES et AUTHENTIQUES.\n"
                "\nRÈGLES STRICTES :\n"
                "1. MAXIMUM 2000 caractères - Concision absolue\n"
                "2. S'appuyer EXCLUSIVEMENT sur le CV fourni - AUCUNE invention\n"
                "3. RÈGLE CRITIQUE: Chaque expérience = 1 chiffre/métrique + 1 résultat\n"
                "   Exemples: \"10k utilisateurs\", \"+40% performant\", \"5 CRM déployés\"\n"
                "4. OBLIGATION: Mention spécifique de l'ENTREPRISE et du SECTEUR\n"
                "5. Intégrer portfolio, email, téléphone si disponibles\n"
                "\nTECHNOLOGIE :\n"
                "- Extraire TOUS les frameworks/langages du CV\n"
                "- Si stack moderne (React/Node/Docker) → mettre EN AVANT\n"
                "- Si stack older (Symfony/Python) → repositionner vers les impacts\n"
                "\nSTRUCTURE OBLIGATOIRE:\n"
                "Para 1: Accroche + Poste + Entreprise (personnalisé)\n"
                "Para 2: Expérience 1 + CHIFFRE\n"
                "Para 3: Expérience 2 + RÉSULTAT\n"
                "Para 4: Expérience 3 + IMPACT\n"
                "Para 5: Formation + Engagement (hackathon, certifs)\n"
                "Para 6: Fermeture + portfolio + contact\n"
                "\nFORMAT :\n"
                "- Texte brut uniquement\n"
                "- Pas d'en-tête\n"
                "- Commence par \"Madame, Monsieur,\"\n"
                "- Ton chaleureux mais professionnel\n"
                "- Phrases COURTES et DIRECTES\n"
                "\nRédige une lettre de motivation unique et humaine pour le poste suivant.\n\n"
                f"POSTE : {offre_titre}\n"
                f"ENTREPRISE : {offre_entreprise}\n"
                f"DÉTAILS OFFRE : {offre_details}\n\n"
                f"MES INFORMATIONS PERSONNELLES :\n{chr(10).join(user_info_parts)}\n\n"
                f"MON CV COMPLET :\n{cv_user['cv_text']}\n\n"
                f"MON CV ANALYSÉ :\n{chr(10).join(cv_parsed_parts)}\n"
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
