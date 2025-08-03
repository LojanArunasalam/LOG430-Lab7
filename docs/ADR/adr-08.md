# 08 - Architectural decision record: Choix de la base de données pour l'Event Store

## Status

Accepté

## Contexte

L'implémentation de l'Event Store nécessite une base de données optimisée pour la persistance des événements. L'Event Store doit gérer un volume important d'écritures (append-only), supporter des requêtes complexes par agrégat, et permettre la reconstruction d'états à partir d'événements.

Les approches possibles incluent :
- PostgreSQL avec colonnes JSONB pour les événements
- MongoDB avec stockage de documents JSON natifs
- EventStore Database spécialisée
- Apache Cassandra pour l'append-only performance

## Décision

Utiliser MongoDB comme base de données pour l'Event Store du Lab 7.

## Justification

- **JSON natif** : Stockage optimal des événements sans conversion ni mapping ORM
- **Schema flexible** : Nouveaux types d'événements sans migration de schéma
- **Performance** : Index spécialisés optimisés pour les patterns Event Sourcing
- **Simplicité d'intégration** : Driver Python Motor pour opérations asynchrones
- **Aggregation Pipeline** : Requêtes analytiques puissantes intégrées

## Conséquences

**Positives :**
- Stockage et requêtes JSON natives sans sérialisation
- Évolution du schéma d'événements sans downtime
- Performance optimale pour reconstruction d'agrégats
- Pipeline d'aggregation pour analytics temps réel
- Scaling horizontal disponible si nécessaire

**Négatives :**
- Moins de garanties ACID strictes que PostgreSQL
- Courbe d'apprentissage pour les développeurs habitués au SQL
- Consommation mémoire plus importante pour les index
- Stratégie de backup différente des bases relationnelles
