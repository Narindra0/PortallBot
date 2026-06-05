# 🚀 Guide de Déploiement Gratuit (100% Sans Votre PC)

Ce guide vous explique comment déployer PortalBot complètement gratuitement, sans avoir à laisser votre ordinateur allumé 24h/24 !

## 📋 Solution Principale: GitHub Actions + Turso
- **GitHub Actions**: pour exécuter automatiquement le scraper toutes les 2h (gratuit)
- **Turso**: pour une base de données SQLite persistante (gratuit)
- **Telegram**: pour recevoir les notifications

---

## 📝 Étape 1: Créer un Repo GitHub
1. Allez sur [GitHub](https://github.com) et créez un nouveau repo (public ou privé)
2. Initialisez Git dans votre projet local (si pas déjà fait):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
3. Ajoutez le remote GitHub et poussez le code:
   ```bash
   git remote add origin https://github.com/VOTRE_NOM_UTILISATEUR/VOTRE_REPO.git
   git branch -M main
   git push -u origin main
   ```

---

## 🗄️ Étape 2: Créer une Base de Données Turso (Optionnel mais Recommandé)
Turso vous permet d'avoir une base de données persistante (sinon les données se perdent entre chaque run GitHub Actions).

1. Créez un compte sur [Turso.tech](https://turso.tech) (gratuit)
2. Installez la CLI Turso ou utilisez le dashboard web pour créer une base de données:
   ```bash
   # Si vous utilisez la CLI
   turso db create portalbot-db
   ```
3. Obtenez l'URL de votre base et un token d'authentification:
   - Dans le dashboard, allez dans votre base → "Settings"
   - Copiez l'URL (ex: `libsql://portalbot-db-utilisateur.turso.io`)
   - Créez un token (Database → Tokens → Create token)

---

## 🔑 Étape 3: Configurer les Secrets GitHub
1. Dans votre repo GitHub, allez dans **Settings** → **Secrets and variables** → **Actions**
2. Cliquez sur **New repository secret** et ajoutez les secrets suivants:

| Nom du Secret               | Valeur                                                                 |
|------------------------------|-----------------------------------------------------------------------|
| `TELEGRAM_TOKEN`             | Votre token bot Telegram (créé avec @BotFather)                       |
| `TELEGRAM_CHAT_ID`           | Votre ID chat Telegram (obtenu avec @userinfobot)                     |
| `GEMINI_API_KEY`             | Votre clé API Google Gemini (https://aistudio.google.com/app/apikey)  |
| `OPENROUTER_API_KEY`         | Votre clé API OpenRouter (https://openrouter.ai)                      |
| `GROQ_API_KEY`                | Votre clé API Groq (https://console.groq.com/keys)                    |
| `TURSO_DATABASE_URL`         | Votre URL Turso (ex: `libsql://...`)                                  |
| `TURSO_AUTH_TOKEN`           | Votre token Turso                                                     |

---

## ⏰ Étape 4: Tester le Workflow GitHub Actions
1. Dans votre repo GitHub, allez dans l'onglet **Actions**
2. Cliquez sur "Scheduled Scraper" (le workflow que nous avons créé)
3. Cliquez sur **Run workflow** → **Run workflow** pour tester manuellement
4. Attendez que le job se termine (quelques minutes)

---

## 📅 Fonctionnement Automatique
- Le scraper s'exécute **toutes les 2 heures** (de 8h à 18h UTC+3, heure de Madagascar)
- Vous recevrez une notification Telegram dès qu'une nouvelle offre IT est trouvée
- Aucun besoin d'avoir votre ordinateur allumé !

---

## 🔍 Vérification et Dépannage
- Voir les logs des runs dans l'onglet **Actions** de votre repo
- Si quelque chose ne fonctionne pas, vérifiez les logs pour les erreurs
- Assurez-vous que tous les secrets sont bien configurés

---

## 💰 Coût Total
- **GitHub Actions**: Gratuit (2000 minutes/mois pour les repos publics, 500 pour les privés)
- **Turso**: Gratuit (500 databases, 1GB storage, 1 billion rows read/mois)
- **Telegram**: Gratuit
- **Total**: 0€ !

---

## 📌 Notes Importantes
- Le workflow est configuré dans `.github/workflows/scheduled-scraper.yml`
- Vous pouvez modifier le cron schedule si vous voulez changer la fréquence
- HEADLESS est configuré à true pour GitHub Actions (pas de navigateur visible)
