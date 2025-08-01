Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard)
# 04 - Architectural decision record

# Choix du cadriciel API pour les services indépendants

## Status

Accepté

## Contexte

Chaque microservice nécessite un framework web léger et performant pour exposer ses APIs REST. Le choix du framework impacte les performances, la maintenabilité et la facilité de développement.

Des options se présentent, comme Django REST Framework, Flask, ou même FastAPI. 

## Décision

Utiliser FastAPI comme framework web pour tous les microservices (Users, Products, Ecommerce, Warehouse).

## Justification

- Performance élevée
- Documentation automatique des APIs (Swagger/OpenAPI)
- Syntaxe moderne et intuitive
- Développement rapide
- Compatible avec l'écosystème Python existant

## Conséquences

**Positives :**
- APIs documentées automatiquement (Documentation OpenAPI déjà existante via url/docs)
- Développement rapide avec validation intégrée
- Excellentes performances
- Facilite les tests d'intégration

**Négatives :**
- Dépendance à un framework relativement récent
- Courbe d'apprentissage pour l'équipe (si non familière avec FastAPI)
