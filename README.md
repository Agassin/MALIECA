# M.A.L.I.E.C.A.

> **My Adaptive Logical Intelligence & Executive Cognitive Assistant**

Projet personnel visant à construire un assistant personnel inspiré de JARVIS, mais réaliste, modulaire et progressivement extensible.

## Vision

M.A.L.I.E.C.A. doit devenir un assistant personnel capable de comprendre des demandes, utiliser des outils, mémoriser le contexte utile, planifier des actions et évoluer progressivement vers une autonomie contrôlée.

L'objectif final est de construire **MALIECA-LLM**, notre propre modèle principal. Les modèles externes, dont Ollama, servent uniquement d'outils temporaires de développement et de validation.

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

### Interface

- [x] CLI
- [x] lancement avec `python -m app.main`
- [x] guide de démarrage

## Démarrage rapide

Le guide complet se trouve dans [`docs/DEMARRAGE.md`](docs/DEMARRAGE.md).

Résumé :

```bash
python -m venv .venv
```

Activer l'environnement virtuel, puis :

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
ollama pull qwen3
python -m app.main
```

Pour vérifier le projet sans Ollama :

```bash
ruff check .
pytest
```

## Architecture actuelle

```text
Utilisateur
    ↓
Interface CLI
    ↓
 Assistant
    ↓
 Runtime
   ↙   ↘
Contexte  ToolRegistry
    ↓         ↓
AIModel    Outils
    ↓         ↑
Ollama ─ Tool Calling
    ↓
Réponse finale
```

Le Runtime ne dépend pas directement d'Ollama. L'adaptateur Ollama implémente `AIModel`, ce qui permettra plus tard de brancher MALIECA-LLM sans réécrire le cœur de l'assistant.

## Roadmap

### Phase 0 — Architecture
- [x] Fondation du cœur
- [x] Système d'outils
- [x] Tool Calling
- [x] Première boucle agentique

### Phase 1 — JARVIS Brain
- [ ] Connecter et tester davantage de modèles locaux temporaires
- [ ] Définir les besoins de MALIECA-LLM
- [ ] Définir le tokenizer
- [ ] Concevoir l'architecture du modèle
- [ ] Préparer les données
- [ ] Entraîner une première version
- [ ] Intégrer MALIECA-LLM dans `AIModel`
- [ ] Retirer progressivement Ollama

### Phase 2 — Mémoire
- [ ] Mémoire court terme structurée
- [ ] Mémoire long terme
- [ ] Recherche dans la mémoire
- [ ] Gestion des préférences

### Phase 3 — Voix
- [ ] Speech-to-text
- [ ] Text-to-speech
- [ ] Wake word
- [ ] Mode conversationnel

### Phase 4 — Outils
- [ ] Nouveaux outils locaux
- [ ] Permissions
- [ ] Validation des arguments
- [ ] Gestion avancée des erreurs

### Phase 5 — Computer Use
- [ ] Fichiers
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

## Structure

```text
MALIECA/
├── app/
│   ├── ai/
│   │   └── providers/
│   ├── core/
│   ├── memory/
│   ├── tools/
│   ├── interfaces/
│   └── main.py
├── tests/
├── docs/
├── .github/workflows/
├── pyproject.toml
└── README.md
```

## Statut

🚧 **Projet en construction — fondation agentique en place.**
