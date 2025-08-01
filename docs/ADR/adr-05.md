# 05 - Architectural decision record: Implémentation du pattern Saga pour la gestion des transactions distribuées

## Status

Accepté

## Contexte

Avec la transition vers une architecture microservices, la gestion des transactions distribuées devient complexe. Les opérations métiers comme la création d'une commande impliquent plusieurs services (Users, Products, Ecommerce, Warehouse) et doivent maintenir la cohérence des données même en cas d'échec partiel.

Les options considérées incluent :
- Transactions distribuées avec 2-Phase Commit (2PC)
- Pattern Saga avec orchestration
- Pattern Saga avec chorégraphie
- Eventual consistency sans garanties transactionnelles

## Décision

Implémenter le pattern Saga avec orchestration centralisée via un service saga-orchestrator dédié.

## Justification

- **Cohérence des données** : Garantit que les opérations complexes s'exécutent complètement ou sont compensées
- **Résilience** : En cas d'échec d'un service, les actions déjà effectuées peuvent être annulées (compensation)
- **Visibilité** : L'orchestrateur centralise la logique métier et facilite le monitoring des transactions
- **Flexibilité** : Permet d'ajouter facilement de nouveaux services dans le workflow
- **Évite la complexité du 2PC** : Plus adapté aux microservices que les transactions distribuées traditionnelles

## Conséquences

**Positives :**
- Garantie de cohérence éventuelle des données
- Meilleure traçabilité des transactions distribuées
- Possibilité de retry automatique en cas d'échec temporaire
- Isolation des échecs par service

**Négatives :**
- Complexité accrue de l'architecture
- Nécessité d'implémenter des actions de compensation pour chaque service
- Point de défaillance unique (le saga orchestrator)
- Latence supplémentaire due aux appels inter-services séquentiels
