# P10

Télécharger/cloner le dépôt P10 (branche master)

Créer un environnement virtuel dans le répertoire P10 créé localement : `python -m venv env`

activer l'environnement virtuel : `source env/bin/activate` (Linux) 
ou `env\\Scripts\\activate.bat` (terminal Windows) 
ou `env\\Scripts\\activate.PS1` (Windows PowerShell)

installer les modules requis à partir du fichier **requirements.txt** : 
`pip install -r requirements`

Se placer dans le dossier **softdesk/**

Y copier le fichier **.env** contenant la SECRET_KEY nécessaire au projet

Pour initialiser la base de données, taper la commande
`python manage.py migrate --run-syncdb`

Lancer le serveur avec la commande `python manage.py runserver`

Pour tester l'API, on peut utiliser l'application Postman.
La documentation de **L'API Project P10 Softdesk API** est consultable
à l'adresse https://documenter.getpostman.com/view/19438945/Uze1uiVU
