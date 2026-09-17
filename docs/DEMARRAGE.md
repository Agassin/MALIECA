# Démarrer M.A.L.I.E.C.A.

Ce guide permet de lancer la version actuelle de M.A.L.I.E.C.A. avec Ollama comme moteur IA temporaire.

> Ollama n'est pas le modèle final de M.A.L.I.E.C.A. Il sert actuellement uniquement à tester le Runtime, les outils et la boucle agentique avant la création de MALIECA-LLM.

## 1. Prérequis

- Python 3.11 ou plus récent
- Git
- Ollama installé et lancé
- un modèle Ollama compatible avec le tool calling

La documentation officielle d'Ollama décrit le tool calling et le cycle agentique :
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

Vérifier qu'Ollama répond :

```bash
ollama list
```

Si le service n'est pas lancé automatiquement, démarrer Ollama avec :

```bash
ollama serve
```

## 6. Vérifier le projet sans Ollama

Les tests utilisent des faux modèles et ne nécessitent pas Ollama :

```bash
pytest
```

Puis vérifier le lint :

```bash
ruff check .
```

Les deux commandes doivent terminer sans erreur.

## 7. Lancer M.A.L.I.E.C.A.

Avec l'environnement virtuel activé :

```bash
python -m app.main
```

Ou :

```bash
python -m app
```

Tu devrais voir :

```text
M.A.L.I.E.C.A. — mode conversation
Moteur : Ollama / qwen3
Tapez 'quit' pour quitter.
> 
```

Tu peux alors tester par exemple :

```text
> Bonjour
> Quelle heure est-il ?
```

Pour quitter :

```text
> quit
```

## 8. Ce qui doit se passer pour un appel d'outil

Pour une demande nécessitant l'outil date/heure, le fonctionnement attendu est :

```text
Utilisateur
    ↓
Runtime
    ↓
Ollama / qwen3
    ↓
Demande d'utilisation de get_current_time
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

Le Runtime limite le nombre d'itérations de la boucle agentique pour éviter une boucle infinie.

## 9. En cas d'erreur Ollama

### « Impossible de contacter Ollama »

Vérifier que le service fonctionne :

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

### Le modèle répond mais n'utilise pas l'outil

Le modèle doit prendre en charge le tool calling. Vérifier le modèle installé et consulter la documentation officielle d'Ollama.

## 10. Vérification complète avant un commit

Exécuter :

```bash
ruff check .
pytest
```

Puis vérifier l'état Git :

```bash
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

Le contrat `AIModel` reste indépendant d'Ollama afin de permettre plus tard l'intégration de MALIECA-LLM.
