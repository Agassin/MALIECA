# Démarrer M.A.L.I.E.C.A.

Ce guide permet de lancer la version actuelle avec Ollama comme moteur IA temporaire.

> Ollama n'est pas le modèle final. Il sert à tester le Runtime, les outils et la boucle agentique avant la création de MALIECA-LLM.

## 1. Prérequis

- Python 3.11 ou plus récent
- Git
- Ollama installé et lancé
- un modèle compatible avec le tool calling

Documentation officielle du tool calling Ollama :
https://docs.ollama.com/capabilities/tool-calling

## 2. Récupérer le projet

```bash
git clone https://github.com/Agassin/MALIECA.git
cd MALIECA
```

## 3. Créer l'environnement Python

Linux/macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 4. Installer M.A.L.I.E.C.A.

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

## 5. Préparer Ollama

Installer Ollama depuis :
https://ollama.com/download

Puis récupérer le modèle utilisé par défaut :

```bash
ollama pull qwen3
```

Vérifier :

```bash
ollama list
```

Si le service n'est pas lancé automatiquement :

```bash
ollama serve
```

## 6. Vérifier le projet sans Ollama

Les tests utilisent des faux modèles et ne nécessitent pas Ollama :

```bash
pytest
ruff check .
```

Les deux commandes doivent terminer sans erreur.

## 7. Lancer M.A.L.I.E.C.A.

Avec l'environnement virtuel activé :

```bash
python -m app.main
```

Tu devrais voir :

```text
M.A.L.I.E.C.A. — mode conversation
Moteur : Ollama / qwen3
Tapez 'quit' pour quitter.
> 
```

Tests simples :

```text
> Bonjour
> Quelle heure est-il ?
```

Pour quitter :

```text
> quit
```

## 8. Test du Tool Calling

Pour une demande nécessitant l'outil date/heure :

```text
Utilisateur
    ↓
Runtime
    ↓
Ollama / qwen3
    ↓
get_current_time
    ↓
ToolRegistry
    ↓
ClockTool
    ↓
Résultat
    ↓
Ollama / qwen3
    ↓
Réponse finale
```

Le Runtime limite le nombre de cycles d'outils afin d'éviter une boucle infinie. Par sécurité, seuls les outils en lecture seule sont exécutés automatiquement. Les outils qui modifient des données ou agissent à l'extérieur sont bloqués jusqu'à l'ajout d'un système de confirmation explicite. Les erreurs d'outils sont renvoyées au modèle sous forme de résultats contrôlés.

## 9. Dépannage

### « Impossible de contacter Ollama »

```bash
ollama list
```

Puis, si nécessaire :

```bash
ollama serve
```

### Modèle absent

```bash
ollama pull qwen3
```

### Le modèle n'utilise pas l'outil

Vérifier que le modèle installé prend en charge le tool calling.

## 10. Vérification avant commit

```bash
ruff check .
pytest
git status
```

## 11. Si Windows ne peut pas créer `.venv`

Si PowerShell indique que `.venv` ou un simple fichier est introuvable/impossible à créer dans le dossier du dépôt, vérifie d'abord que le dossier accepte l'écriture. Ne supprime pas le dépôt existant. Tu peux faire un clone de test dans un emplacement accessible, par exemple :

```powershell
git clone https://github.com/Agassin/MALIECA.git D:\\MALIECA-test
cd D:\\MALIECA-test
py -3.12 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

Puis reprends l'installation à l'étape 4. Ce clone est indépendant du dossier initial.

## 12. Évaluer le tokenizer expérimental

Depuis la racine du dépôt, après installation du projet :

```powershell
python scripts/evaluer_tokenizer.py
```

Le script affiche le nombre d'octets, le nombre de tokens, la taille du vocabulaire, les fusions apprises et la vérification de réversibilité. Il entraîne sur un corpus synthétique et mesure sur un second corpus tenu à part. Les résultats ne constituent pas un benchmark de qualité représentatif.

## 13. Conception de MALIECA-LLM

Le cadrage technique initial, les hypothèses de tokenizer et de modèle, les règles de données et les critères de validation sont documentés dans [`CONCEPTION_MALIECA_LLM.md`](CONCEPTION_MALIECA_LLM.md). Les choix de taille du modèle et d'entraînement restent ouverts jusqu'à l'inventaire du matériel.

## Architecture actuelle

```text
Interface CLI
     ↓
  Assistant
     ↓
   Runtime
  ↙       ↘
Contexte  ToolRegistry
     ↓         ↓
  Ollama    Outils
     ↘       ↙
    Tool Calling
        ↓
 Réponse finale
```

Le contrat `AIModel` reste indépendant d'Ollama afin de permettre l'intégration future de MALIECA-LLM.
