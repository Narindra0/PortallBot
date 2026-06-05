"""
Module de nettoyage automatique et surveillance de la mémoire pour PortalBot.
- Nettoyage après chaque requête
- Nettoyage périodique
- Surveillance de l'utilisation mémoire
- Preserve les données persistantes (BDD, config, logs, CV)
"""

import gc
import os
import time
import psutil
import tempfile
from datetime import datetime, timedelta
from typing import Optional
from Bot.utils.logger import logger
from Bot.config import (
    BASE_DIR,
    LOG_DIR,
    LOCAL_DB_PATH,
    CV_PDF_PATH,
    PORTAL_SESSION_PATH,
    ASAKO_SESSION_PATH
)

# === Configuration ===
# Seuil de temps de réponse max (ms) pour exécuter le nettoyage après une requête
MAX_RESPONSE_TIME_FOR_CLEANUP = 2000  # 2 secondes
# Seuil mémoire pour déclencher un nettoyage forcé (MB)
MEMORY_THRESHOLD_MB = 500
# Âge max des fichiers temporaires avant suppression (heures)
TEMP_FILE_MAX_AGE_HOURS = 24
# Liste des chemins à protéger (jamais supprimés !)
PROTECTED_PATHS = [
    LOCAL_DB_PATH,
    CV_PDF_PATH,
    PORTAL_SESSION_PATH,
    ASAKO_SESSION_PATH,
    os.path.join(BASE_DIR, "config"),
    os.path.join(BASE_DIR, ".env"),
]

# Variables globales non persistentes (pour réinitialisation)
GLOBAL_TEMP_VARS = {
    "last_request_timestamp": 0.0,
    "temp_letter_content": None,
    "temp_cv_data": None,
    "temp_offer_data": None,
}

def get_memory_usage() -> float:
    """
    Retourne l'utilisation mémoire du processus en MB.
    """
    try:
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        return mem_info.rss / (1024 * 1024)  # RSS en MB
    except Exception as e:
        logger.warning(f"Impossible de récupérer l'utilisation mémoire : {e}")
        return 0.0

def log_memory_usage(context: str = "") -> None:
    """
    Enregistre l'utilisation mémoire dans les logs.
    """
    mem_mb = get_memory_usage()
    if context:
        logger.info(f"📊 Mémoire utilisée {context} : {mem_mb:.2f} MB")
    else:
        logger.info(f"📊 Mémoire utilisée : {mem_mb:.2f} MB")

def force_gc() -> None:
    """
    Force le garbage collector Python et libère la mémoire allouée dynamiquement.
    """
    try:
        gc.collect()
        gc.collect()  # Double collecte pour être sûr
        logger.debug("♻️ Garbage Collector exécuté avec succès")
    except Exception as e:
        logger.warning(f"Erreur lors du garbage collect : {e}")

def reset_global_temp_vars() -> None:
    """
    Réinitialise les variables globales non persistentes.
    """
    global GLOBAL_TEMP_VARS
    GLOBAL_TEMP_VARS = {
        "last_request_timestamp": 0.0,
        "temp_letter_content": None,
        "temp_cv_data": None,
        "temp_offer_data": None,
    }
    logger.debug("🔄 Variables temporaires globales réinitialisées")

def cleanup_temp_files() -> None:
    """
    Supprime les fichiers temporaires obsolètes, sans toucher aux données persistantes.
    """
    cleaned_count = 0
    current_time = time.time()
    max_age_seconds = TEMP_FILE_MAX_AGE_HOURS * 3600

    # Nettoyer le répertoire temporaire système
    temp_dir = tempfile.gettempdir()
    try:
        for root, _, files in os.walk(temp_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    # Vérifier si le fichier est protégé (éviter tout accident !)
                    is_protected = False
                    for protected in PROTECTED_PATHS:
                        if os.path.commonpath([filepath, protected]) == os.path.abspath(protected):
                            is_protected = True
                            break
                    if is_protected:
                        continue

                    # Vérifier l'âge du fichier
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        cleaned_count += 1
                except Exception:
                    continue
        if cleaned_count > 0:
            logger.info(f"🧹 {cleaned_count} fichiers temporaires obsolètes supprimés")
    except Exception as e:
        logger.warning(f"Erreur lors du nettoyage des fichiers temporaires : {e}")

    # Nettoyer les fichiers temporaires dans le répertoire du projet (si existants)
    project_temp_extensions = [".tmp", ".temp", ".cache"]
    try:
        for root, _, files in os.walk(BASE_DIR):
            # Sauter les dossiers à protéger
            for protected in PROTECTED_PATHS:
                if os.path.isdir(protected) and os.path.commonpath([root, protected]) == os.path.abspath(protected):
                    break
            else:
                for filename in files:
                    filepath = os.path.join(root, filename)
                    try:
                        # Vérifier si le fichier est protégé
                        is_protected = False
                        for protected in PROTECTED_PATHS:
                            if os.path.abspath(filepath) == os.path.abspath(protected):
                                is_protected = True
                                break
                        if is_protected:
                            continue

                        # Vérifier l'extension et l'âge
                        if any(filename.endswith(ext) for ext in project_temp_extensions):
                            file_age = current_time - os.path.getmtime(filepath)
                            if file_age > max_age_seconds:
                                os.remove(filepath)
                                cleaned_count += 1
                    except Exception:
                        continue
    except Exception as e:
        logger.warning(f"Erreur lors du nettoyage des fichiers temporaires du projet : {e}")

def cleanup_after_request(start_time: float) -> None:
    """
    Nettoyage à exécuter après chaque requête utilisateur.
    Vérifie si le temps écoulé est inférieur au seuil pour préserver la réactivité.
    """
    elapsed_ms = (time.time() - start_time) * 1000
    mem_mb = get_memory_usage()

    # Toujours logger l'utilisation mémoire
    log_memory_usage(f"(après requête, {elapsed_ms:.0f} ms)")

    # Vérifier si on doit exécuter le nettoyage
    should_cleanup = False
    if mem_mb > MEMORY_THRESHOLD_MB:
        should_cleanup = True
        logger.info(f"🧹 Déclenchement nettoyage (mémoire > {MEMORY_THRESHOLD_MB} MB)")
    elif elapsed_ms < MAX_RESPONSE_TIME_FOR_CLEANUP:
        should_cleanup = True
        logger.debug(f"🧹 Nettoyage après requête (temps réponse OK)")
    else:
        logger.debug("⏭️ Nettoyage sauté pour préserver la réactivité")

    if should_cleanup:
        force_gc()
        reset_global_temp_vars()
        # Nettoyage des fichiers temporaires uniquement périodiquement (pas à chaque requête)
        pass

def full_cleanup() -> None:
    """
    Nettoyage complet (à exécuter périodiquement, pas à chaque requête).
    """
    logger.info("🧹 Début du nettoyage complet...")
    start_time = time.time()

    log_memory_usage("(avant nettoyage)")

    # 1. Garbage Collector
    force_gc()

    # 2. Réinitialiser variables temporaires
    reset_global_temp_vars()

    # 3. Nettoyer fichiers temporaires
    cleanup_temp_files()

    # 4. Logger la mémoire après nettoyage
    log_memory_usage("(après nettoyage)")

    elapsed = (time.time() - start_time) * 1000
    logger.info(f"✅ Nettoyage complet terminé en {elapsed:.0f} ms")

def check_and_cleanup() -> None:
    """
    Vérifie l'état et déclenche un nettoyage si nécessaire.
    """
    mem_mb = get_memory_usage()
    if mem_mb > MEMORY_THRESHOLD_MB:
        logger.warning(f"⚠️ Mémoire élevée : {mem_mb:.2f} MB > {MEMORY_THRESHOLD_MB} MB")
        full_cleanup()
