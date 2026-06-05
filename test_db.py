#!/usr/bin/env python3
"""
Script de test pour la base de données SQLite de PortalBot.
Vérifie l'initialisation, les migrations et les opérations CRUD.
"""
import asyncio

from Bot.config import LOCAL_DB_PATH
from Bot.storage.cache_db import (
    compter_offres_async,
    init_db_async,
    lister_offres_permanentes_async,
    offre_existe_async,
    recuperer_cv_async,
    sauvegarder_cv_async,
    sauvegarder_offre_permanente_async,
)


async def test_database():
    print("=" * 60)
    print("TEST DE LA BASE DE DONNEES PORTALBOT")
    print("=" * 60)

    # Étape 1: Initialiser la DB
    print("\n[1/6] Initialisation de la base de données...")
    await init_db_async()
    print("[OK] Initialisation réussie!")

    # Étape 2: Tester sauvegarde CV
    print("\n[2/6] Test de sauvegarde du CV...")
    await sauvegarder_cv_async(
        nom="Test User",
        email="test@example.com",
        telephone="0123456789",
        portfolio="https://portfolio.example.com",
        cv_text="Développeur Python avec 3 ans d'expérience..."
    )
    print("[OK] CV sauvegardé!")

    # Étape 3: Tester récupération CV
    print("\n[3/6] Test de récupération du CV...")
    cv = await recuperer_cv_async()
    if cv:
        print(f"[OK] CV récupéré: {cv['nom']} ({cv['email']})")
        print(f"   Portfolio: {cv['portfolio']}")
        print(f"   CV Texte: {cv['cv_text'][:50]}...")
    else:
        print("[ERREUR] Échec de la récupération du CV!")
        return

    # Étape 4: Tester sauvegarde offre
    print("\n[4/6] Test de sauvegarde d'une offre...")
    test_offre = {
        "url": "https://example.com/job/123",
        "titre": "Développeur Python (Test)",
        "entreprise": "Test Corp",
        "date_publication": "2026-06-04",
        "details": "Offre de test pour PortalBot...",
        "date_decouverte": "2026-06-04 12:00:00",
        "linkedin_url": "https://linkedin.com/company/test-corp",
        "facebook_url": None,
        "website_url": "https://test-corp.example.com"
    }
    await sauvegarder_offre_permanente_async(test_offre)
    print("[OK] Offre sauvegardée!")

    # Étape 5: Vérifier si l'offre existe
    print("\n[5/6] Vérification de l'existence de l'offre...")
    exists = await offre_existe_async(test_offre["url"])
    if exists:
        print("[OK] Offre trouvée dans la base!")
    else:
        print("[ERREUR] Offre non trouvée!")
        return

    # Étape 6: Lister les offres et compter
    print("\n[6/6] Test de listing et comptage des offres...")
    count = await compter_offres_async()
    offres = await lister_offres_permanentes_async()
    print(f"[OK] Nombre d'offres: {count}")
    for idx, offre in enumerate(offres):
        print(f"   {idx+1}. {offre['titre']} @ {offre['entreprise']}")

    print("\n" + "=" * 60)
    print("TOUS LES TESTS ONT REUSSI!")
    print(f"Fichier DB: {LOCAL_DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_database())
