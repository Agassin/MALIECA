# M.A.L.I.E.C.A.

> **My Adaptive Logical Intelligence & Executive Cognitive Assistant**

Projet personnel visant à construire un assistant personnel inspiré de JARVIS, mais réaliste, modulaire et progressivement extensible.

## Vision

M.A.L.I.E.C.A. doit devenir un assistant personnel capable de comprendre des demandes, utiliser des outils, mémoriser le contexte utile, planifier des actions et évoluer progressivement vers une autonomie contrôlée.

**La version 0.2 propose un assistant local utilisable dans le terminal ou le navigateur.**
Ollama reste le moteur conversationnel par défaut. Le premier prototype de **MALIECA-LLM**,
le modèle maison, peut être entraîné sur CPU puis chargé par le même assistant.

## Principes

1. **Modulaire** — chaque capacité est isolée dans un module.
2. **Indépendant du modèle** — le cœur communique avec les modèles via `AIModel`.
3. **Local-first quand c'est pertinent** — limiter les dépendances inutiles.
4. **Sécurité** — aucune clé ou donnée sensible dans le dépôt.
5. **Testable** — les fonctionnalités importantes sont testées sans dépendre d'un service externe.
6. **Évolutif** — construire les fondations avant les fonctionnalités avancées.

## État actuel

### Fondation

- [x] `AIModel`
- [x] `ConversationContext`
- [x] `Runtime`
- [x] `Assistant`
- [x] `Tool`
- [x] `ToolRegistry`
- [x] outil date/heure
- [x] niveaux de risque des outils
- [x] tests avec faux modèle
- [x] adaptateur Ollama
- [x] CI GitHub Actions

### Boucle agentique

- [x] contrat abstrait de Tool Calling
- [x] représentation des appels d'outils
- [x] transmission des schémas d'outils au modèle
- [x] boucle `modèle → outil → résultat → modèle`
- [x] limite contre les boucles infinies
- [x] Tool Calling natif avec Ollama
- [x] tests du Tool Calling
- [x] exécution automatique limitée aux outils en lecture seule
- [x] blocage des outils modificateurs sans autorisation
- [x] gestion contrôlée des outils inconnus et des exceptions
- [x] validation stricte des arguments d'outils (types, champs requis, champs inconnus et bornes simples)
- [x] prototype de tokenizer BPE au niveau des octets
- [x] tests d'encodage/décodage, de reproductibilité et de sauvegarde du tokenizer
- [x] métriques d'évaluation BPE et script de démonstration
- [x] Transformer causal et entraînement supervisé avec validation distincte
- [x] checkpoint expérimental chargé derrière `AIModel`
- [x] mémoire SQLite, notes, tâches modifiables et recherche dans les documents texte importés

### Interface

- [x] CLI
- [x] interface web locale et API JSON sur l'adresse de bouclage
- [x] lancement avec `python -m app.main`
- [x] guide de démarrage

## Démarrage rapide

Le guide complet se trouve dans [`docs/DEMARRAGE.md`](docs/DEMARRAGE.md).

Avec Python 3.11+ et Ollama installé, depuis un environnement virtuel activé :

```bash
python -m pip install -e .
ollama pull qwen3
python -m app.main
```

- `python -m app.main --web` sert l'interface sur http://127.0.0.1:8765/.
- `python -m app.main --offline` donne accès aux commandes locales sans modèle ni Ollama.
- Tapez `/aide` pour les commandes. Par exemple, `/tache ajouter Relire le dossier`,
  `/tache modifier 1 Relire le chapitre`, `/note chercher` ou `/document importer notes.md`.
- Par défaut, l'historique, les notes, les tâches et les textes importés restent dans
  `~/.malieca/memory.sqlite3`. L'option `--db CHEMIN` permet d'utiliser une autre base.

Pour entraîner puis charger le modèle expérimental sur CPU :

```bash
python -m pip install -e ".[llm]"
python scripts/entrainer_malieca.py
python -m app.main --checkpoint .data/malieca-demo.pt
```

Le corpus de démonstration vérifie que l'entraînement et la génération fonctionnent.
La génération sur des demandes nouvelles reste peu fiable. Le prototype répond en texte.

Pour évaluer le prototype BPE sur son corpus synthétique :

```bash
python scripts/evaluer_tokenizer.py
```

Ce résultat est un contrôle technique initial, pas un benchmark représentatif.

Pour vérifier le projet sans Ollama :

```bash
python -m pip install -e '.[dev]'
ruff check .
python -m pytest
```

## Sécurité actuelle du Runtime

Le Runtime ne présente au modèle et n'exécute automatiquement que les outils `READ_ONLY`.
L'utilisateur peut modifier ses données avec les commandes explicites dans les deux interfaces.
Les documents importés sont consultables par l'outil de recherche. Un serveur Ollama configuré
avec `--ollama-url` reçoit les messages et les résultats d'outils nécessaires à la conversation. Les outils qui modifient des données ou déclenchent une action externe sont bloqués tant qu'un mécanisme de confirmation explicite n'est pas disponible. Les arguments sont validés avant l'exécution (types, champs requis, propriétés inconnues et contraintes simples). Les outils inconnus et les exceptions sont convertis en résultats d'erreur contrôlés.

Cette protection est volontairement restrictive : elle évite qu'un modèle puisse déclencher une action non autorisée simplement en produisant un appel d'outil.

## Architecture actuelle

```text
Utilisateur
    ↓
CLI ou web local
    ↓
 Assistant
    ↓
 Runtime
   ↙   ↘
Contexte et mémoire  ToolRegistry
    ↓         ↓
AIModel    Outils
    ↓         ↑
Ollama / MALIECA-LLM
    ↓
Réponse finale
```

Le Runtime ne dépend pas directement d'Ollama. L'adaptateur Ollama implémente `AIModel`, tout comme l'adaptateur expérimental de MALIECA-LLM.

## Roadmap

### Phase 0 — Architecture
- [x] Fondation du cœur
- [x] Système d'outils
- [x] Tool Calling
- [x] Première boucle agentique

### Phase 1 — JARVIS Brain
- [ ] Relever et documenter le matériel de développement
- [x] Cadrage initial de MALIECA-LLM (`docs/CONCEPTION_MALIECA_LLM.md`)
- [x] Premier protocole de mesure du tokenizer (corpus synthétique)
- [ ] Évaluer le tokenizer sur un corpus français représentatif et documenté
- [x] Tester le Tool Calling sur un serveur Ollama local avec Qwen3
- [x] Première configuration structurelle du Transformer (`app/ai/models/config.py`)
- [x] Implémenter et tester le forward pass causal du petit Transformer sur CPU
- [x] Entraîner un prototype sur le corpus de démonstration documenté
- [x] Intégrer le prototype de génération dans `AIModel`
- [ ] Élargir le corpus français et code et vérifier les licences
- [ ] Évaluer le suivi des consignes et le Tool Calling de MALIECA-LLM
- [ ] Retirer progressivement Ollama

### Phase 2 — Mémoire
- [x] Contexte de conversation et historique persistant
- [x] Notes personnelles explicites et tâches stockées localement
- [x] Recherche textuelle dans les notes et documents importés
- [ ] Recherche sémantique par embeddings et gestion structurée des préférences

### Phase 3 — Voix
- [ ] Speech-to-text
- [ ] Text-to-speech
- [ ] Wake word
- [ ] Mode conversationnel

### Phase 4 — Outils
- [x] Outils locaux de lecture pour l'heure, les tâches, les notes et les documents importés
- [x] Validation des arguments et récupération après un tour interrompu
- [ ] Confirmations d'actions système, isolation et journal d'audit

### Phase 5 — Computer Use
- [x] Import explicite de fichiers texte et recherche dans leur contenu
- [ ] Gestion de fichiers avec permissions
- [ ] Terminal
- [ ] Applications
- [ ] Navigateur

### Phase 6 — Vision
- [ ] Analyse d'image
- [ ] Compréhension de l'écran

### Phase 7 — Agent autonome
- [ ] Planification
- [ ] Exécution multi-étapes
- [ ] Vérification
- [ ] Auto-correction contrôlée

### Phases 8 et 9 — Automatisation et agents spécialisés
- [ ] Exécution planifiée, notifications et surveillance
- [ ] Orchestration et agrégation de résultats de plusieurs agents

## Structure

```text
MALIECA/
├── app/
│   ├── ai/
│   │   ├── providers/
│   │   ├── tokenizers/
│   │   └── models/
│   ├── core/
│   ├── memory/
│   ├── tools/
│   │   └── validation.py
│   ├── interfaces/
│   └── main.py
├── data/demo/
├── tests/
├── scripts/
│   ├── entrainer_malieca.py
│   └── evaluer_tokenizer.py
├── docs/
├── .github/workflows/
├── pyproject.toml
└── README.md
```

## Statut

**Version locale 0.2.** L'objectif JARVIS 1.0 reste en développement.
