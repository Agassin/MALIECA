# M.A.L.I.E.C.A

> **My Adaptive Logical Intelligence & Executive Cognitive Assistant**

Projet personnel visant à construire un assistant personnel inspiré de JARVIS, mais réaliste et progressivement extensible.

## Vision

M.A.L.I.E.C.A. doit devenir une interface intelligente capable d'aider à :

- organiser et exécuter des tâches ;
- interagir avec des outils et services ;
- automatiser des actions répétitives ;
- rechercher et synthétiser des informations ;
- mémoriser le contexte utile ;
- fournir une interface vocale et textuelle ;
- évoluer progressivement vers un véritable assistant personnel.

## Principes

1. **Modulaire** — chaque capacité est isolée dans un module.
2. **Local-first quand c'est pertinent** — limiter les dépendances inutiles.
3. **Sécurité** — aucune clé ou donnée sensible dans le dépôt.
4. **Testable** — chaque fonctionnalité importante doit être vérifiable.
5. **Évolutif** — commencer simple avant d'ajouter des capacités complexes.

## Roadmap

### Phase 0 — Fondation
- [ ] Architecture du projet
- [ ] Environnement Python
- [ ] Configuration centralisée
- [ ] Logging
- [ ] Tests
- [ ] Documentation

### Phase 1 — Assistant texte
- [ ] Interface CLI
- [ ] Boucle conversationnelle
- [ ] Gestion du contexte
- [ ] Commandes locales

### Phase 2 — Outils
- [ ] Système de plugins/outils
- [ ] Gestionnaire de tâches
- [ ] Recherche web
- [ ] Automatisations

### Phase 3 — Mémoire
- [ ] Mémoire court terme
- [ ] Mémoire long terme
- [ ] Recherche dans la mémoire
- [ ] Gestion des préférences

### Phase 4 — Voix
- [ ] Speech-to-text
- [ ] Text-to-speech
- [ ] Wake word
- [ ] Mode conversationnel

### Phase 5 — Orchestration
- [ ] Planification d'actions
- [ ] Exécution multi-étapes
- [ ] Vérification des résultats
- [ ] Gestion des erreurs

## Structure cible

```text
MALIECA/
├── app/
│   ├── core/
│   ├── agents/
│   ├── memory/
│   ├── tools/
│   ├── interfaces/
│   └── config/
├── tests/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Statut

🚧 Projet en construction.
