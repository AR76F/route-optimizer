# Manager Setup Guide

This document explains how to install, launch, and perform basic maintenance of the AI Service Coordinator Assistant. Also a special foreword for Patrice.

---

# Intro

Salut Patrice, j'espère que tu vas bien. Tout est en place pour un petit test à l'interne dans le département du service. Le chatbot possède ces fonctions clées: mémoire de conversation, connexion avec un modèle OpenAI GPT pour son raisonnement, une version simplifiée de Retrieval Augmented Generation (RAG), capacité d'analyser des images (OCR). Le reste de ce document contient les étapes pour que tu sois capable de tester le chatbot sur ton propre ordinateur. 

---

Je voulais aussi noter des particuliarités importantes sur le chatbot que les gens du service devraient en tenir compte lors de leurs essais.

- Le bot est meilleur en anglais qu'en français, c'est la nature d'un bot lié à un modèle GPT de OpenAI. La majorité du training data de OpenAI est en anglais. 
- Pour envoyer une image dans le chatbot, on doit téléverser un fichier. On ne peut pas copier-coller directement dans le boite de conversation. Je pourrais modifier cela plus tard.
- Le coût des tokens par question tend à monter vite lorsqu'une conversation contient une image (ou plusieurs). Donc il est primordial de supprimer les images lorsqu'on en n'a plus de besoin. On peut continuer la conversation tout de même ou simplement recommencer une nouvelle conversation.
- Parlant des coûts de tokens, en temps normal, ils restent sous contrôle et n'ont pas explosé après avoir intégré la fonction image.
- Il faut abosulement donner le plus de contexte possible lors qu'on pose une question au chatbot. Sinon, le chatbot ne peut pas aller chercher les infos correctement dans la base de données. Son "retrieval" dépend beaucoup sur des mots clés, donc sans eux, le chatbot va buguer.
- L'important est évidemment de recevoir le plus grand nombre possible de feedback des gens du service pour vraiment savoir qu'est-ce qu'il est important pour eux. 

# Initial Setup

## 1. Clone the Repository

Clone the GitHub repository to your local computer.

```bash
git clone https://github.com/UD016/route-optimizer-assistant
```

---

## 2. Open the Project

Open the project folder using Visual Studio Code.

---

## 3. Create a Python Virtual Environment

```bash
python -m venv myenv
```

---

## 4. Activate the Environment

### Windows

```bash
myenv\scripts\activate
```

---

## 5. Install Required Packages

```bash
pip install -r requirements.txt
```

---

## 6. Configure the OpenAI API Key

Create a `.env` file in the project root or configure the **user** environment variable (recommended)

Example:

```text
OPENAI_API_KEY = your_api_key_here
```

> **Note:** The API key is not stored in the GitHub repository and must be provided separately.

---

## 7. Launch the Application

```bash
python -m streamlit run app.py
```

The application will automatically open in your default web browser.

---

# Updating the Project

To retrieve the latest changes from GitHub:

```bash
git pull
```

If new Python packages have been added:

```bash
pip install -r requirements.txt
```

---

# Updating the Knowledge Base

Most updates only require editing or adding Markdown files inside the `knowledge_base/` folder.

Typical examples include:

- New procedures
- Updated technician profiles
- New troubleshooting guides
- Internal process changes

After making changes, restart the Streamlit application if required.

---

