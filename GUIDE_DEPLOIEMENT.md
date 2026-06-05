# Guide de Déploiement Complet PortalBot

Ce guide explique comment déployer PortalBot pour qu'il soit en ligne 24h/24 !

---

## 📋 Prérequis
Avant de commencer, tu dois avoir :
1. Ton code PortalBot sur un repo GitHub
2. Un bot Telegram créé avec @BotFather (tu as le token)
3. Ton ID chat Telegram (récupéré avec @userinfobot)
4. Les clés API :
   - Google Gemini → https://aistudio.google.com/app/apikey
   - OpenRouter → https://openrouter.ai/keys
   - Groq → https://console.groq.com/keys
5. Une base de données Turso → https://turso.tech (URL + token)

---

## 🛠️ 1. Pousser le code sur GitHub
Dans ton terminal (dossier du projet) :
```bash
git add .
git commit -m "Configuration complète PortalBot"
git push origin main
```

---

## 🎯 2. Choisis une plateforme de déploiement
Tu as le choix entre 4 plateformes (toutes avec un plan gratuit) :

---

### Option A : Railway (Recommandé)
#### Étapes :
1. Allez sur https://railway.app → crée un compte
2. Clique sur **New Project** → **Deploy from repo**
3. Choisis ton repo PortalBot → **Deploy Now**
4. Dans ton projet Railway → onglet **Variables** → ajoute TOUTES ces variables :
   | Nom de la Variable          | Valeur                                                                 |
   |------------------------------|-----------------------------------------------------------------------|
   | `TELEGRAM_TOKEN`             | Ton token bot Telegram                                                 |
   | `TELEGRAM_CHAT_ID`           | Ton ID chat Telegram                                                   |
   | `GEMINI_API_KEY`             | Ta clé Gemini                                                          |
   | `OPENROUTER_API_KEY`         | Ta clé OpenRouter                                                      |
   | `GROQ_API_KEY`               | Ta clé Groq                                                            |
   | `TURSO_DATABASE_URL`         | Ton URL Turso (ex: `libsql://...`)                                     |
   | `TURSO_AUTH_TOKEN`           | Ton token Turso                                                        |
   | `HEADLESS`                   | `true`                                                                 |
5. Attends le déploiement (quelques minutes) → ton bot est en ligne !

---

### Option B : Northflank
#### Étapes :
1. Allez sur https://app.northflank.com/ → crée un compte
2. Clique sur **Create Project** → donne un nom → choisis une région
3. Clique sur **Create New** → **Service** → **Combined Service**
4. Choisis **Git Repository** → connecte GitHub → choisis ton repo → branche `main`
5. Choisis **Use a Dockerfile** → chemin `Dockerfile`
6. Dans **Environment Variables** → ajoute toutes les variables (même que Railway)
7. Clique sur **Create** → attends le déploiement !

---

### Option C : Back4App
#### Étapes :
1. Allez sur https://dashboard.back4app.com/ → crée un compte
2. Clique sur **Containers** → **Build and deploy new app**
3. Choisis **Deploy from GitHub repository** → choisis ton repo → branche `main`
4. Vérifie **Dockerfile** → chemin `./Dockerfile`
5. Dans **Environment Variables** → ajoute toutes les variables (même que Railway)
6. Clique sur **Deploy** → attends le déploiement !

---

### Option D : Render
#### Étapes :
1. Allez sur https://render.com/ → crée un compte
2. Clique sur **New** → **Web Service** (ou **Background Worker**)
3. Choisis ton repo GitHub → branche `main`
4. Choisis **Docker** comme Environment
5. Dans **Environment Variables** → ajoute toutes les variables (même que Railway)
6. Choisis le plan **Starter** → clique sur **Create Web Service**

---

## 🔍 3. Vérifie que ça marche
1. Ouvre Telegram → envoye `/start` à ton bot
2. Teste les commandes : `/configurer_cv`, `/voir_cv`, `/aide`
3. Vérifie les logs de la plateforme pour confirmer qu'il n'y a pas d'erreurs
4. Attends les prochaines offres scrapées → tu recevras une notification !

---

## ⏰ 4. GitHub Actions (Scraper Planifié)
Le workflow **Scheduled Scraper** est déjà configuré pour s'exécuter toutes les 2h (de 8h à 18h UTC+3).

Pour vérifier/configurer :
1. Allez sur ton repo GitHub → onglet **Actions**
2. Choisis **Scheduled Scraper** → tu peux lancer manuellement avec **Run workflow**
3. Pour modifier le planning : édite `.github/workflows/scheduled-scraper.yml` → change la valeur `cron:`

---

## 📚 Documentation supplémentaire
- README.md → Explication du projet et des fonctionnalités
- DEPLOY.md → Ancien guide (pas à jour, mais peut être utile)

---

## ❓ Aide
Si tu as des problèmes :
1. Vérifie les logs de la plateforme de déploiement
2. Vérifie que toutes les variables d'environnement sont correctes
3. Vérifie que Turso est bien configuré
4. Vérifie que le token Telegram est valide

Bon déploiement ! 🚀
