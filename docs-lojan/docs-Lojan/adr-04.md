Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard) 

# ADR-04 - Architectural decision record

# Choix du système de traitement des tâches en arrière-plan

## Status

Accepté

## Contexte

OpenProject nécessite un système robuste pour traiter les tâches en arrière-plan telles que :
- L'envoi d'emails de notification
- La génération de rapports et exports
- Le traitement de fichiers volumineux
- La synchronisation avec des systèmes externes (LDAP, Git, etc.)
- Les tâches de maintenance et de nettoyage
- L'indexation pour la recherche

L'application doit gérer un volume important de tâches avec des exigences de fiabilité élevées, particulièrement dans des environnements d'entreprise où la perte de données est critique.

Trois options principales ont été évaluées :
1. **Sidekiq** - Solution basée sur Redis, très performante
2. **Delayed Job** - Solution basée sur la base de données, simple
3. **Good Job** - Solution moderne basée sur PostgreSQL

## Décision

Good Job a été choisi comme système de traitement des tâches en arrière-plan pour OpenProject.

## Justification

Good Job présente des avantages significatifs pour OpenProject, particulièrement en termes d'intégration avec l'infrastructure existante. L'**intégration PostgreSQL native** constitue l'un des principaux atouts de cette solution, car elle utilise la même base de données que l'application principale, éliminant ainsi le besoin d'infrastructure supplémentaire comme Redis. En effet Good Job s'intègre parfaitement avec Rails et ActiveJob, utilise PostgreSQL déjà choisi pour l'application, et bénéficie d'un développement actif avec une communauté croissante, garantissant un support à long terme.


## Conséquences
- Réduction des coûts d'infrastructure avec PostgreSQL. 
- Fiabilité maximale sans risque de perte de jobs 
- Charge lourde sur la base de données
