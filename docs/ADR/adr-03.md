Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard) 
# 03 - Architectural decision record

# Transition vers une architecture microservices

## Status

Accepté

## Contexte

L'architecture monolithique actuelle présente des limitations de performance sous charge élevée et des difficultés de maintenance avec l'augmentation de la complexité du système. La croissance en fonctionnalités deviendrait alors un problème. 

Des architectures comme microservices, architecture orientée services, ou même une architecture orientée évènements. 

## Décision

Accepté pour microservices. Migrer vers une architecture microservices avec séparation des domaines métiers : Users, Products, Ecommerce, et Warehouse.

## Justification

- Amélioration des performances sous charge (démontrée par les tests Locust)
- Scalabilité horizontale par service
- Séparation des responsabilités selon les domaines métiers
- Facilite le développement parallèle par équipes

## Conséquences

**Positives :**
- Meilleure performance et résilience
- Évolutivité indépendante des services
- Isolation des pannes

**Négatives :**
- Complexité opérationnelle accrue (configuration de api gateway)
- Besoin d'outils de monitoring distribué
