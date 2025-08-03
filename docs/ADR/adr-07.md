# 07 - Architectural decision record: Choix du message broker pour l'architecture Event-Driven

## Status

Accepté

## Contexte

L'implémentation de l'architecture event-driven nécessite un message broker pour la communication asynchrone entre microservices. Le système doit supporter la publication d'événements, la souscription par patterns, le routage intelligent, et la persistance des messages pour la fiabilité.

Les approches possibles incluent :
- RabbitMQ avec exchanges et routing flexible
- Apache Kafka pour high-throughput et event streaming
- Redis Streams pour simplicité et performance
- Amazon SQS/SNS pour solution managed cloud

## Décision

Utiliser RabbitMQ comme message broker principal pour l'architecture event-driven du Lab 7.

## Justification

- **Simplicité** : Setup rapide avec Docker et configuration minimale
- **Fiabilité** : Persistance des messages et acknowledgments garantis
- **Routing flexible** : Exchanges (topic, direct, fanout) pour patterns complexes
- **Observabilité** : Management UI complète pour monitoring temps réel
- **Intégration Python** : Librairie pika robuste et bien documentée

## Conséquences

**Positives :**
- Configuration et déploiement rapides pour environnement de lab
- Interface de monitoring intuitive pour debugging et observabilité
- Support complet des patterns Pub/Sub et routing par événements
- Persistance garantie et gestion des échecs intégrée
- Écosystème Python mature avec documentation extensive

**Négatives :**
- Performance moindre que Kafka pour très gros volumes de messages
- Single point of failure sans configuration en cluster
- Consommation mémoire importante avec accumulation de messages
- Scaling limité comparé aux solutions cloud natives
**Documentation** : Très bien documenté  
**Communauté** : Large adoption, support actif  
**Performance** : Suffisante pour le volume du lab  
**Pédagogie** : Concepts clairs, interface intuitive  

### Négatives
**Scaling limité** : Moins performant que Kafka pour très gros volumes  
**Single point of failure** : Nécessite clustering pour HA  
**Mémoire** : Peut consommer beaucoup de RAM avec de gros volumes  



