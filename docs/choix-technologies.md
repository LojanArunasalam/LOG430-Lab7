# Tableau de choix de technologies
Voici un tableau qui démontre les technologies utilisées dans ce système

| Element | Technologie | Justification |
| --- | ----------- | -------------- | 
| Language | Python | Facile à utiliser
| Web Framework | Django | Framework très populaire permettant l'architecture MVC, et une évolution vers une utilisation d'API
| ORM | SQLAlchemy | Mécanisme de persistence bien documenté dans Python
| Base de données | PostgreSQL | Robuste et offre plus de fonctionnalités que SQLite et n'est pas en local
| Conteneurisation | Docker | Conteneuriser l'application, pour pouvoir la rouler dans la VM de production
| CI/CD | Github Actions | Automatiser le processus de test et déploiement après des changements effectués dans le code