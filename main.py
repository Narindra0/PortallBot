#!/usr/bin/env python3
"""
PortalBot - Point d'entrée principal (Async)
"""
import asyncio
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from Scraper.portal import surveiller_portal
from Scraper.asako import surveiller_asako
from Scraper.mission_mada import surveiller_mission_mada
from Bot.callback_handler import setup_application
from Bot.storage.cache_db import init_db_async
from Bot.utils.logger import logger
from Bot.utils.cleanup import full_cleanup, log_memory_usage

async def run_scraper_task(bot):
    """Encapsulation de la tâche scraper pour le scheduler."""
    try:
        # Lancement simultané des scrapers (PortalJob + Asako + Mission-Mada)
        await asyncio.gather(
            surveiller_portal(telegram_bot=bot),
            surveiller_asako(telegram_bot=bot),
            surveiller_mission_mada(telegram_bot=bot)
        )
    except Exception as e:
        logger.error(f"Erreur durant la tâche planifiée : {e}")

async def main():
    """Point d'entrée principal asynchrone."""
    # Analyse des arguments
    mode = "all"
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()

    logger.info(f"🚀 Initialisation du système (Mode: {mode})...")
    
    # Log mémoire initiale
    log_memory_usage("(démarrage)")
    
    # 1. Initialisation Base de données
    await init_db_async()
    
    # 2. Configuration du Bot
    app = setup_application()
    if not app:
        logger.error("❌ Impossible de configurer le bot Telegram. Vérifie config/.env")
        return

    # Initialiser l'application bot
    await app.initialize()
    
    # --- Mode SCRAPER (exécution unique) ---
    if mode == "scraper":
        logger.info("🔍 Lancement du scan ponctuel (PortalJob + Asako + Mission-Mada)...")
        try:
            await asyncio.gather(
                surveiller_portal(telegram_bot=app.bot),
                surveiller_asako(telegram_bot=app.bot),
                surveiller_mission_mada(telegram_bot=app.bot)
            )
            logger.info("✅ Scan terminé avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur durant le scan : {e}")
        finally:
            await app.shutdown()
        return

    # --- Mode BOT-ONCE (pour GitHub Actions - une seule itération) ---
    if mode == "bot-once":
        logger.info("🤖 Mode bot-once: exécution unique pour GitHub Actions...")
        try:
            await app.start()
            # Exécuter un scan unique
            await run_scraper_task(app.bot)
            logger.info("✅ Bot-once terminé avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur durant bot-once : {e}")
        finally:
            await app.stop()
            await app.shutdown()
        return

    # --- Modes permanents (BOT ou ALL) ---
    await app.start()
    
    scheduler = None
    if mode in ["all", "combined"]:
        # 3. Configuration du Scheduler (Toutes les 2 heures de 08h à 18h)
        scheduler = AsyncIOScheduler()
        scheduler.add_job(run_scraper_task, 'cron', hour='8,10,12,14,16,18', minute=0, args=[app.bot])
        # Ajouter le job de nettoyage complet toutes les 6 heures
        scheduler.add_job(full_cleanup, 'cron', hour='*/6', minute=30)
        scheduler.start()
        logger.info("📅 Scheduler démarré (08h00 - 18h00, toutes les 2h)")
        logger.info("🧹 Nettoyage complet programmé toutes les 6 heures")
        
        # Lancement d'un scan immédiat
        asyncio.create_task(run_scraper_task(app.bot))

    # Lancement du Bot en mode polling
    logger.info("🤖 Bot en ligne et prêt !")
    try:
        # On utilise l'updater pour le polling
        await app.updater.start_polling(drop_pending_updates=True)
        
        # Garder le programme en vie
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("👋 Arrêt du système...")
    except Exception as e:
        if "Conflict" in str(e):
             logger.error("❌ Conflit détecté : Vérifie qu'aucune autre instance du bot ne tourne !")
        else:
             logger.error(f"❌ Erreur inattendue : {e}")
    finally:
        # Arrêt propre
        logger.info("⏳ Fermeture des services...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        if scheduler:
            scheduler.shutdown()
        
        pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        if pending:
            await asyncio.wait(pending, timeout=5.0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
