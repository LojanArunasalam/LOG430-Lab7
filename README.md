## LOG430-Lab5

# Architecture de l'application 
![Architecture de l'application](images/image.png)

# Lancer le projet 
1. Se placer sur le root directory
```
cd src/app
python manage.py runserver
```

# Lancer le conteneur
1. Se placer sur le root directory et rouler la base de données
```
docker compose up -d db
```
2. Effectuer 3 splits du terminal, et rouler une dans chaque terminal
```
docker compose run --rm django-client
```
# Lancer les tests
```
pytest src/app/caisse/tests.py
```
