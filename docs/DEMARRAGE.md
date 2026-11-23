# Démarrer M.A.L.I.E.C.A.

M.A.L.I.E.C.A. fonctionne dans le terminal ou le navigateur. Ollama est le moteur par défaut.

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
Tapez /aide pour les commandes et quit pour quitter.
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

## 14. Interface web, historique et fichiers

```powershell
python -m app.main --web
```

Ouvrez http://127.0.0.1:8765/. Le service écoute uniquement sur la boucle locale IPv4.
`--port` permet de changer le port. Ajoutez `--offline` pour accéder aux données locales
sans lancer Ollama.

Exemples de commandes à saisir dans le terminal ou dans le champ de l'interface web :

```text
/tache ajouter Relire la documentation
/tache modifier 1 Relire le guide de démarrage
/tache terminer 1
/tache liste
/note ajouter Le français est ma langue préférée.
/note chercher langue
/document importer C:\Documents\Projet été.md
/document chercher objectif
/historique
```

Le fichier de données se trouve dans `~/.malieca/memory.sqlite3` ou à l'emplacement
indiqué par `--db`. Le moteur reçoit les 12 derniers échanges terminés. Les commandes et
les appels d'outils intermédiaires ne sont pas conservés dans l'historique.
`/historique effacer` efface les échanges de cette base. Les commandes `/note supprimer`
et `/document supprimer` permettent de retirer les notes et les copies indexées par identifiant.

L'index accepte les fichiers UTF-8 `.txt`, `.md` et `.rst` jusqu'à 1 Mio. Il retrouve
des passages par mots-clés et fournit leur document et leur numéro. L'import stocke une
copie des passages dans SQLite. Réimporter le même fichier actualise cette copie.

`--model` sélectionne un modèle Ollama installé. L'option `--ollama-url` permet de choisir
un serveur. Les messages et résultats d'outils sont transmis à ce serveur, dont l'adresse
est locale par défaut. Pour couper les fonctions cloud d'Ollama, utilisez son mode local.

## 15. Entraîner le prototype MALIECA-LLM

```powershell
python -m pip install -e ".[llm]"
python scripts/entrainer_malieca.py
python -m app.main --checkpoint .data/malieca-demo.pt
```

Le script utilise une configuration CPU de démonstration. Il apprend le tokenizer sur
l'entraînement, mesure la perte et la compression sur un fichier séparé, puis enregistre les
poids et les paramètres. Les options `--train`, `--validation`, `--output`, `--steps` et
`--seed` permettent de reproduire ou d'adapter l'expérience. Utilisez des checkpoints produits
par le script ou provenant d'une source approuvée.

Le jeu de démonstration vérifie la capacité du petit modèle à apprendre et à générer du texte.
Le Tool Calling de l'assistant est assuré par Ollama.
