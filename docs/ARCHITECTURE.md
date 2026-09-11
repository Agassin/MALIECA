# Architecture M.A.L.I.E.C.A.

## 1. Vision

M.A.L.I.E.C.A. est un assistant personnel IA modulaire. Il doit pouvoir comprendre une demande, conserver le contexte utile, choisir des capacités, exécuter des actions contrôlées, vérifier leurs résultats puis répondre à l'utilisateur.

Le projet s'inspire des architectures observées dans plusieurs projets open source d'assistants et d'agents, sans copier leur implémentation. Les références principales étudiées sont Mem0 pour la mémoire persistante, Open WebUI pour les concepts de mémoire/skills, et plusieurs assistants JARVIS/open-source pour les pipelines voix, outils et contrôle ordinateur.

## 2. Architecture cible

```text
                         USER
                           │
                 ┌─────────▼─────────┐
                 │     INTERFACE     │
                 │ CLI / Voice / UI  │
                 └─────────┬─────────┘
                           │ UserMessage
                 ┌─────────▼─────────┐
                 │   AGENT RUNTIME   │
                 │                   │
                 │  Context Builder  │
                 │  Reasoner         │
                 │  Planner          │
                 │  Tool Router      │
                 │  Verifier         │
                 └──────┬───────┬────┘
                        │       │
              ┌─────────▼─┐   ┌─▼─────────┐
              │  MEMORY   │   │   TOOLS   │
              │           │   │           │
              │ Working   │   │ Files     │
              │ Episodic  │   │ Terminal  │
              │ Semantic  │   │ Web       │
              │ Procedural│   │ Apps/API  │
              └───────────┘   └───────────┘
                        │       │
                        └───┬───┘
                            │
                    ┌───────▼────────┐
                    │ SECURITY LAYER  │
                    │ permissions     │
                    │ confirmation    │
                    │ audit           │
                    │ sandbox         │
                    └───────┬────────┘
                            │
                    Local system / APIs
```

## 3. Principes de conception

- Le Core ne dépend d'aucune interface utilisateur.
- Le fournisseur LLM est interchangeable derrière une abstraction `AIModel`.
- Une capacité est exposée comme un outil explicite avec entrée, sortie et niveau de risque.
- La mémoire est séparée du raisonnement : le modèle ne doit pas être la base de données.
- Les actions sensibles passent par une couche de permissions avant exécution.
- Toute exécution importante produit un résultat observable et vérifiable.
- Les intégrations externes sont optionnelles : le noyau doit rester utilisable en local.
- On préfère une implémentation simple et testable à une architecture agentique prématurée.

## 4. Cycle agentique

```text
REQUEST
   ↓
PERCEPTION
   ↓
CONTEXT BUILDING ← Memory
   ↓
REASONING ← AIModel
   ↓
PLANNING
   ↓
TOOL SELECTION
   ↓
PERMISSION CHECK
   ↓
EXECUTION → Tool
   ↓
OBSERVATION
   ↓
VERIFICATION
   ├── succès → réponse / étape suivante
   └── échec  → correction / nouvelle tentative / arrêt contrôlé
```

Une conversation simple ne doit pas forcément lancer une boucle agentique complète. Le runtime choisit le niveau de complexité nécessaire.

## 5. Modules

```text
app/
├── core/          # domaine et orchestration
│   ├── assistant.py
│   ├── runtime.py
│   ├── models.py
│   └── events.py
├── ai/             # abstraction et adaptateurs LLM
│   ├── base.py
│   └── providers/
├── memory/         # stockage et récupération du contexte
│   ├── working.py
│   ├── episodic.py
│   ├── semantic.py
│   └── store.py
├── tools/          # capacités exécutables
│   ├── base.py
│   ├── registry.py
│   └── builtin/
├── security/       # permissions, confirmations, audit
├── interfaces/     # CLI, puis voix et UI
├── config/         # configuration et secrets
└── main.py
```

## 6. Mémoire

M.A.L.I.E.C.A. adoptera une progression en trois niveaux avant d'ajouter une base vectorielle complexe :

1. **Working memory** : conversation courante et état d'exécution.
2. **Episodic memory** : sessions et événements importants.
3. **Semantic memory** : faits, préférences, projets et connaissances récupérables.

Une solution de type Mem0 pourra être utilisée comme composant optionnel après validation, notamment pour l'extraction et la recherche de souvenirs. Le stockage local doit rester possible.

## 7. Tools

Tous les outils suivent une interface commune :

```text
Tool
├── name
├── description
├── input_schema
├── risk_level
└── execute(input) -> ToolResult
```

Le modèle choisit un outil ; il ne reçoit jamais un accès direct arbitraire au système.

## 8. Sécurité

Niveaux prévus :

- `0` : lecture sans effet de bord
- `1` : action réversible locale
- `2` : modification locale
- `3` : action externe ou publication
- `4` : action critique

Les niveaux 3 et 4 nécessitent une confirmation explicite par défaut. Les outils système seront progressivement sandboxés.

## 9. Open source : stratégie

Nous réutilisons les idées et bibliothèques open source lorsqu'elles réduisent réellement le temps de développement :

- **Mem0** : mémoire persistante et recherche de souvenirs.
- **Open WebUI** : concepts de skills, mémoire durable et workflows.
- **Assistants JARVIS open source** : patterns voix, outils système, computer use et fallback de modèles.
- **Outils MCP** lorsque leur protocole apporte une interface standard pour des capacités externes.

M.A.L.I.E.C.A. conserve cependant son propre Core, ses contrats d'interface et son système de permissions afin de ne pas devenir dépendant d'un seul framework.

## 10. Ordre d'implémentation

### A — Foundation
- [x] structure du projet
- [x] CLI séparée du Core
- [x] tests de base
- [x] CI
- [ ] configuration typée
- [ ] logging structuré

### B — Brain minimal
- [ ] `AIModel` abstraction
- [ ] `ConversationContext`
- [ ] runtime simple
- [ ] premier adaptateur LLM
- [ ] tool calling abstrait

### C — Tools
- [ ] registry
- [ ] outil temps/date
- [ ] filesystem sécurisé
- [ ] terminal contrôlé
- [ ] web

### D — Memory
- [ ] working memory
- [ ] SQLite episodic store
- [ ] semantic memory
- [ ] retrieval
- [ ] intégration Mem0 optionnelle

### E — Agent
- [ ] planner
- [ ] executor
- [ ] verifier
- [ ] retry/correction
- [ ] permissions

### F — Voice / Vision / Computer Use
- [ ] STT
- [ ] TTS
- [ ] wake word
- [ ] vision
- [ ] computer use

### G — Autonomy
- [ ] scheduler
- [ ] tâches multi-étapes
- [ ] notifications
- [ ] multi-agent spécialisé
