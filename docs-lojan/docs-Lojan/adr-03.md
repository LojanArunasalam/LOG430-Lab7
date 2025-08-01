Template tirée de [Documenting architecture decisions - Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions) venant de [Github](https://github.com/joelparkerhenderson/architecture-decision-record/tree/main/locales/en/templates/decision-record-template-by-michael-nygard) 
# 01 - Architectural decision record

# Choix du framework frontend

## Status

Accepté

## Contexte

OpenProject nécessitait une refonte de son interface utilisateur pour offrir une expérience moderne et interactive. L'ancienne interface basée uniquement sur du HTML/ERB côté serveur présentait des limitations :
- Interactivité limitée (rechargements de page fréquents)
- Difficultés pour créer des interfaces complexes (tableaux dynamiques, formulaires avancés)
- Performance dégradée avec de gros volumes de données
- Expérience utilisateur moins fluide

Plusieurs options étaient envisageables : Angular, React, Vue.js, ou conserver une approche Rails traditionnel avec du JavaScript vanilla.

## Décision

Nous avons choisi Angular comme framework frontend principal pour OpenProject, en maintenant une architecture hybride avec Rails côté backend.

## Justification

1. **TypeScript natif** : 
   - Typage statique améliorant la qualité du code
   - Meilleure maintenabilité pour une large base de code
   - Détection d'erreurs à la compilation

2. **Architecture structurée** :
   - Injection de dépendances intégrée
   - Séparation claire des responsabilités (services, composants, modules)
   - Conventions bien établies pour les gros projets

3. **Écosystème riche** :
   - CLI puissant pour la génération de code
   - Testing intégré (Jasmine, Karma)
   - Outils de développement avancés

4. **Performance** :
   - Change detection optimisée
   - Lazy loading des modules
   - AOT compilation pour la production

5. **Intégration avec Rails** :
   - API REST bien supportée
   - Possibilité de migration progressive
   - Coexistence avec les vues Rails existantes

6. **Communauté et support** :
   - Framework maintenu par Google
   - Documentation complète
   - Communauté active et mature

## Conséquences

**Positives :**
- Interface utilisateur plus réactive et moderne
- Meilleure séparation frontend/backend
- Développement parallèle des équipes front/back
- Performance améliorée pour les interactions complexes
- Base de code frontend plus maintenable

**Négatives :**
- Complexité accrue de l'architecture
- Courbe d'apprentissage pour l'équipe
- Bundle JavaScript plus volumineux
- Deux environnements de développement à maintenir
- Potentiels problèmes de SEO pour certaines pages

**Risques atténués :**
- Formation de l'équipe sur Angular et TypeScript
- Migration progressive par modules
- Maintien du server-side rendering pour les pages publiques
- Tests automatisés côté frontend
