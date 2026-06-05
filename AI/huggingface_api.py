"""
Module de connexion à l'API Hugging Face pour génération de lettres de motivation.
Support Async avec gestion d'erreurs, retry exponentiel et compatibilité URL globale.
"""
import re
from huggingface_hub import InferenceClient
from Bot.config import HF_API_KEY
from Bot.utils.logger import logger

# Modèle 100% Gratuit (Serverless Inference API)
HF_MODEL = "Qwen/Qwen2.5-7B-Instruct"

def nettoyer_reponse_ai(text):
    """
    Nettoie les réponses de l'IA pour Telegram (HTML).
    Supprime les blocs <think> (pensées de DeepSeek) et les tags non supportés.
    """
    if not text: return ""
    
    # 1. Supprimer les blocs <think> complets (Insensible à la casse)
    text = re.sub(r'<(think)>.*?</\1>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. Supprimer un début de <think> orphelin (si réponse tronquée)
    text = re.sub(r'<(think)>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # 3. Supprimer tout tag HTML non supporté par Telegram (b, i, a, code, pre)
    # On capture tout ce qui n'est pas dans la liste blanche
    text = re.sub(r'<(?!/?(b|i|a|code|pre)\b)[^>]+>', '', text, flags=re.IGNORECASE)
    
    # 4. Nettoyage résiduel
    text = text.replace('**', '').replace('---', '').strip()
    
    return text

async def generer_lettre_motivation_async(cv_text, offre_titre, offre_entreprise, offre_details, portfolio=""):
    """Génère une lettre de motivation via l'API Hugging Face Free Serverless."""
    if not HF_API_KEY:
        logger.error("HF_API_KEY manquante.")
        return None

    try:
        # Initialisation du client (plus robuste qu'une URL manuelle)
        client = InferenceClient(api_key=HF_API_KEY)
        
        context_portfolio = f"Voici mon portfolio pour appuyer ma candidature : {portfolio}" if portfolio else ""
        
        system_prompt = (
            "Tu es un expert en recrutement rédigeant des lettres de motivation percutantes, professionnelles et authentiques.\n"
            "\nRÈGLES STRICTES :\n"
            "1. Produis une lettre de motivation de bonne qualité, concise et percutante (pas trop longue pour ne pas lasser les recruteurs), avec une structure claire et des arguments ciblés sur le poste visé.\n"
            "2. S'appuie EXCLUSIVEMENT sur les informations contenues dans le CV fourni. Ne jamais ajouter d'expérience, compétence ou réalisation non mentionnée dans le CV.\n"
            "3. Vérifie systématiquement que TOUTES les informations dans la lettre correspondent EXACTEMENT à des éléments présents dans le CV fourni. Aucune information inventée !\n"
        )
        
        user_prompt = (
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

        # Utilisation du Chat Completion via le client (gère les URLs automatiquement)
        response = client.chat.completions.create(
            model=HF_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1024,
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
    if not HF_API_KEY: return None

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