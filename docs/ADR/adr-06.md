# 06 - Architectural decision record: Choix de la machine à états pour la gestion du workflow Saga

## Status

Accepté

## Contexte

L'implémentation du pattern Saga nécessite une gestion rigoureuse des états et des transitions. Le workflow d'une commande passe par plusieurs étapes (validation stock, réservation, paiement) et doit pouvoir gérer les échecs et compensations à chaque étape.

Les approches possibles incluent :
- Machine à états simple avec if/else
- Framework de workflow externe (Temporal, Zeebe)
- Machine à états custom avec persistance en base
- Event sourcing avec projection d'états

## Décision

Implémenter une machine à états custom avec persistance des états en base de données PostgreSQL.

## Justification

- **Simplicité** : Contrôle total sur la logique métier sans dépendance externe
- **Persistance** : Les états sont sauvegardés, permettant la reprise après redémarrage
- **Traçabilité** : Historique complet des transitions d'états pour audit
- **Performance** : Pas de latence réseau vers des services externes
- **Intégration** : S'intègre naturellement avec l'écosystème Python/PostgreSQL existant

## Conséquences

**Positives :**
- Contrôle total sur la logique de workflow
- Debugging facilité grâce à la persistance des états
- Performance optimale (pas de dépendance réseau)
- Coût réduit (pas de licence de workflow engine)

**Négatives :**
- Maintenance du code de machine à états à notre charge
- Pas de fonctionnalités avancées des workflow engines (retry policies complexes, scheduling)
- Risque de bugs dans l'implémentation custom
- Effort de développement plus important qu'avec une solution existante