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
- [x] exécution automatique limitée aux outils en lecture seule
- [x] blocage des outils modificateurs sans autorisation
- [x] gestion contrôlée des outils inconnus et des exceptions
- [x] prototype de tokenizer BPE au niveau des octets
- [x] tests d'encodage/décodage, de reproductibilité et de sauvegarde du tokenizer
- [x] métriques d'évaluation BPE et script de démonstration

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

Pour évaluer le prototype BPE sur son corpus synthétique :

```bash
python scripts/evaluer_tokenizer.py
```

Ce résultat est un contrôle technique initial, pas un benchmark représentatif.

Pour vérifier le projet sans Ollama :

```bash
ruff check .
pytest
```

## Sécurité actuelle du Runtime

Le Runtime ne présente au modèle et n'exécute automatiquement que les outils `READ_ONLY`. Les outils qui modifient des données ou déclenchent une action externe sont bloqués tant qu'un mécanisme de confirmation explicite n'est pas disponible. Les outils inconnus et les exceptions sont convertis en résultats d'erreur contrôlés.

Cette protection est volontairement restrictive : elle évite qu'un modèle puisse déclencher une action non autorisée simplement en produisant un appel d'outil.

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
- [ ] Relever et documenter le matériel de développement
- [x] Cadrage initial de MALIECA-LLM (`docs/CONCEPTION_MALIECA_LLM.md`)
- [x] Premier protocole de mesure du tokenizer (corpus synthétique)
- [ ] Évaluer le tokenizer sur un corpus français représentatif et documenté
- [ ] Connecter et tester davantage de modèles locaux temporaires
- [ ] Concevoir l'architecture du modèle
- [ ] Sélectionner des données autorisées et documenter leurs licences
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
│   │   ├── providers/
│   │   └── tokenizers/
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
