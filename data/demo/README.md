# Corpus de démonstration

Les 60 dialogues courts ont été générés pour cette démonstration. Ils contiennent des exemples
fictifs en français et des commandes de MALIECA. Aucun document tiers et aucune donnée
personnelle n'ont été utilisés comme source. Leur utilisation pour entraîner ou évaluer le
prototype est autorisée dans le cadre de MALIECA.

- `train.jsonl` contient 48 exemples et sert à apprendre le tokenizer et les poids.
- `validation.jsonl` contient 12 demandes distinctes, dont des reformulations de thèmes vus
  pendant l'apprentissage. Il sert à suivre la perte et la compression du tokenizer.
- Les deux fichiers utilisent un objet JSON par ligne, avec les champs `user` et `assistant`.

La taille et la proximité des exemples limitent l'expérience à la vérification du pipeline.
Un benchmark de généralisation nécessite un corpus plus large et un jeu de test indépendant.
