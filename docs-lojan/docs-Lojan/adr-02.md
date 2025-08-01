Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard) 
# 02 - Architectural decision record

# Implémentation des mécanismes d'authentification.

## Status

Accepté

## Contexte

De nombreux informations sensibles sont utilisées lors des fonctionnalités dans OpenProject, tels que les sessions cookies, les logins via username et mot de passe et aussi les jetons d'accès pour les APIs. Des mauvaises configurations de mécanismes d'authentification présentent des risques majeurs: 
- Accès non-authorisé d'un attaqueur.
- Attaques de type force brute
- Vole d'informations d'identification et compromis d'un compte.

Il est donc important de mettre en place des mécanismes pour sécuriser l'ensemble de l'application.
## Décision
 
Les algorithmes et mécanismes utilisées afin de combler les failles présentées dans le contexte ont été choisies:
- BCrypt est utilisé comme algorithme de hachage pour mot de passe 
- Authentification externes tels que LDAP, OpenID connect et SAML 2.0 
- L'utilisation d'OAuth 2.0 pour les accès API 

## Justification

Ces mécanismes et algorithmes ont été choisis car, ensemble, ils offrent une sécurité renforcée et efficace contre les attaques par force brute, en rendant ces dernières beaucoup plus coûteuses à exécuter. De plus, les données sensibles sont désormais mieux protégées, ce qui permet au système de se conformer aux normes de sécurité en vigueur dans l'industrie.

## Conséquences

- La gestion de l'ensemble de l'authentification devient une tache complexe de plus (ajouter du loggings pour les erreurs et les tentatives d'attaques)
-
