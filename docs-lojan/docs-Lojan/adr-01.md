Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard) 
# 01 - Architectural decision record

# Choix d'un cadriciel MVC 

## Status

Accepté

## Contexte

OpenProject est une application web de gestion de projets qui offre plusieurs fonctionnalités, comme le suivi des tâches, la gestion des utilisateurs, des rôles et des permissions, la visualisation avec des diagrammes de Gantt, ainsi que bien d'autres outils utiles.

Pour rendre cela possible, il faut adopter une architecture modulaire basée sur un cadriciel MVC. Ce type de cadriciel facilite un développement rapide et met à disposition de nombreuses bibliothèques, ressources et un bon support pour répondre aux différents besoins du système.

Des options s'offrent à nous quant aux choix de cadriciels, tels que Django, Ruby on Rails, Spring. 

## Décision
 
Ruby on Rails a été choisi comme cadriciel pour MVC 

## Justification

La raison pour laquelle Ruby on Rails a été choisi comme cadriciel MVC est car il permet un développement rapide grâce à son ORM intégré. De plus, il facilite l’étalement horizontal des applications, ce qui est utile pour la montée en charge. Rails bénéficie aussi d’un grand écosystème, avec de nombreux outils, librairies, ressources et un bon support de la communauté. Enfin, comme Ruby on Rails suit le principe DRY (Don't Repeat Yourself), il limite la répétition de code. Cela rend les applications plus faciles à maintenir, à faire évoluer et à comprendre sur le long terme. 

## Conséquences

- Système plus maintenable et flexible
- Developpement rapide et facilement étalable.
- La librairie Ruby OpenSSL X509 est utilisé pour effectuer des connections externes (Base de données, LDAP, etc) sur des  conteneurs ayant des encryptions SSL. 
- Les mécanismes de sécurité du cadriciel sont utilisés pour prévenir les attaques d'injection et les attaques CSRF. Des mesures de sécurité sont mises en places, comme l'encodage propre de l'HTML, l'usage des tokens, et l'échappement automatique des queries SQL.