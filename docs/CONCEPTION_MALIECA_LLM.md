# Conception de MALIECA-LLM

> Document de cadrage initial. Les choix ci-dessous sont des hypothèses de travail à valider par des prototypes, pas des spécifications figées.

## 1. Objectif

Construire un modèle de langage développé dans le cadre du projet M.A.L.I.E.C.A., intégrable derrière le contrat Python `AIModel`.

Le modèle doit progressivement apprendre à :
- comprendre et produire du français ;
- suivre des consignes ;
- conserver une structure de conversation ;
- produire des appels d'outils conformes à un schéma ;
- fonctionner localement, sans API d'IA propriétaire obligatoire.

**Point de réalisme :** entraîner un petit modèle à partir de zéro est un objectif pédagogique et technique accessible par étapes. Entraîner seul un modèle généraliste comparable aux grands modèles actuels demanderait des volumes de données, de calcul et de financement hors de portée d'un projet individuel classique. Le premier modèle ne sera donc pas présenté comme un assistant généraliste performant.

## 2. Périmètre de la première version

La première version doit être volontairement limitée :
1. tokenizer reproductible ;
2. petit modèle Transformer autorégressif ;
3. entraînement reproductible sur un corpus documenté ;
4. génération de texte ;
5. tests automatiques et mesures de qualité ;
6. adaptateur Python implémentant `AIModel`.

Le Tool Calling viendra après la maîtrise de la génération de texte. Il nécessitera un format de sortie structuré, des exemples dédiés et des évaluations spécifiques.

## 3. Architecture proposée

### 3.1 Modèle

Hypothèse initiale : Transformer décodeur uniquement, entraîné en prédiction du prochain token.

Composants à prototyper :
- embeddings de tokens ;
- encodage positionnel ;
- blocs d'attention causale multi-têtes ;
- réseaux feed-forward ;
- normalisation ;
- projection vers le vocabulaire ;
- fonction de perte cross-entropy.

Aucune taille définitive n'est choisie avant l'inventaire du matériel et un benchmark mémoire/temps.

### 3.2 Tokenizer

Hypothèse de départ : Byte Pair Encoding (BPE). Un premier prototype éducatif au niveau des octets existe dans `app/ai/tokenizers/bpe.py`. Il est déterministe, sans dépendance externe et possède des tests d'encodage/décodage et de sauvegarde. Il n'est pas encore optimisé ni validé sur un corpus représentatif.

La cible expérimentale de vocabulaire reste à étudier ; 8 000 tokens est une hypothèse pour une version ultérieure, pas la taille actuelle du prototype (512 par défaut).

Contraintes :
- corpus de tokenizer séparé des jeux d'évaluation ;
- conservation des accents, de la ponctuation et des caractères français ;
- traitement explicite des espaces et retours à la ligne ;
- tokens spéciaux distincts pour début/fin de message et rôles ;
- sauvegarde de la configuration et du vocabulaire avec chaque checkpoint.

Un premier script de mesure est disponible avec `python scripts/evaluer_tokenizer.py`. Il utilise un corpus synthétique écrit pour le projet et rapporte le nombre d'octets, le nombre de tokens, le nombre de fusions, les octets par token et la réversibilité. Ce contrôle vérifie le pipeline, mais ne permet pas de conclure sur la qualité d'un tokenizer en production.\n\nLa prochaine évaluation devra utiliser un corpus français, du code et des commandes plus représentatifs, avec provenance/licences documentées et séparation entre apprentissage et évaluation. La taille du vocabulaire sera révisée après cette mesure.

### 3.3 Format conversationnel

Le format d'entraînement devra représenter sans ambiguïté :
- système ;
- utilisateur ;
- assistant ;
- appel d'outil ;
- résultat d'outil ;
- fin de tour.

Les tokens spéciaux et leur sérialisation devront être identiques entre l'entraînement, les tests et l'adaptateur d'inférence.

## 4. Données et licences

Aucun corpus ne sera intégré avant vérification de sa provenance et de ses conditions d'utilisation.

Règles :
- privilégier les textes du domaine public, les corpus explicitement ouverts et les données produites par le projet ;
- conserver la source, la licence, la date de collecte et les transformations ;
- exclure les données personnelles et les secrets ;
- dédupliquer les documents ;
- séparer entraînement, validation et test ;
- ne jamais entraîner sur le jeu de test ;
- documenter les limites et les biais connus.

La quantité de données ne remplacera pas la qualité, la diversité et la légalité des sources.

## 5. Évaluation

Chaque expérience doit être reproductible et enregistrer :
- version du code ;
- version du tokenizer ;
- sources et empreintes des données ;
- paramètres d'entraînement ;
- matériel utilisé ;
- durée, mémoire et consommation estimée ;
- métriques sur validation ;
- exemples de générations avec prompts fixes.

Mesures initiales :
- perte d'entraînement et de validation ;
- perplexité lorsque sa comparaison est pertinente ;
- qualité linguistique sur un jeu de prompts fixe ;
- respect des consignes simples ;
- stabilité de génération ;
- plus tard : exactitude du format d'appel d'outil.

Une baisse de perte ne prouve pas à elle seule qu'un modèle est utile ou sûr.

## 6. Sécurité et intégration

Le modèle ne doit jamais exécuter lui-même une action système. Il propose une sortie structurée ; le Runtime décide si l'outil existe et si son niveau de risque autorise l'exécution.

Principes :
- les outils en lecture seule peuvent être exécutés automatiquement ;
- les outils qui modifient des données ou agissent à l'extérieur restent bloqués tant qu'un mécanisme d'autorisation explicite n'existe pas ;
- les arguments devront être validés côté application avant exécution ; ils ne sont jamais considérés comme fiables parce que le modèle les a produits ;
- les erreurs d'outils sont renvoyées au modèle comme résultats contrôlés ;
- une limite d'itérations empêche les boucles infinies.

## 7. Phases et critères de sortie

| Phase | Livrable | Critère de validation |
|---|---|---|
| 0 | Inventaire matériel et objectifs | CPU, RAM, GPU, VRAM et stockage connus |
| 1 | Prototype tokenizer | première implémentation BPE et tests de réversibilité présents ; benchmark représentatif restant à faire |
| 2 | Petit Transformer | formes, masquage causal et forward pass testés |
| 3 | Pipeline de données | sources/licences documentées, splits sans fuite |
| 4 | Entraînement minimal | perte qui converge sur un petit corpus contrôlé |
| 5 | Évaluation | résultats reproductibles et limites publiées |
| 6 | Adaptateur `AIModel` | tests contractuels identiques aux autres modèles |
| 7 | Tool Calling expérimental | schémas valides, erreurs gérées et actions protégées |

Chaque phase doit pouvoir être arrêtée ou redimensionnée si les contraintes matérielles ou les résultats ne sont pas satisfaisants.

## 8. Informations manquantes avant l'entraînement

Il faut relever sur la machine de développement :
- modèle exact du processeur ;
- quantité de RAM ;
- carte graphique et quantité de VRAM ;
- espace disque disponible ;
- système d'exploitation et version de Python.

Tant que ces informations ne sont pas connues, il serait prématuré de choisir une taille de modèle, un batch size ou une durée d'entraînement.

## 9. Décisions ouvertes

- taille finale du vocabulaire ;
- taille et nombre de couches du premier modèle ;
- framework d'entraînement ;
- corpus autorisés et objectifs linguistiques ;
- stratégie de fine-tuning éventuelle ;
- format exact des messages et appels d'outils.

Ces décisions seront prises à partir de mesures, et non sur des estimations arbitraires.
