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
py -3.11 -m venv .venv
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

Le Runtime limite le nombre d'itérations afin d'éviter une boucle infinie.

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
