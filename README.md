P10

Télécharger/cloner le dépôt P10 (branche master)

Créer un environnement virtuel dans le répertoire P10 créé localement : python -m venv env

activer l'environnement virtuel : source env/bin/activate (Linux) ou env\\Scripts\\activate.bat (terminal Windows) ou env\\Scripts\\activate.PS1 (Windows PowerShell)

installer les modules requis à partir du fichier requirements.txt : pip install -r requirements

Se placer dans le dossier softdesk/

Y copier le fichier .env contenant la SECRET_KEY nécessaire au projet

Lancer le serveur avec la commande python manage.py runserver

Ouvrir le navigateur internet à l'adresse http://127.0.0.1:8000/login/
Conformité à la PEP8

La conformité des scripts du projet à la PEP8 peut être vérifiée en utilisant le wrapper flake8.
Pour ce faire, se placer à la racine du projet (P10) et lancer la commande flake8 softdesk/
Remarque :

Hors démonstration, ce projet ne comporte aucune donnée (pas de migration, ni table SQLite)

L'utilisateur/développeur qui installe les fichiers du présent projet doit donc exécuter la commande suivante pour initialiser la base de données :

python manage.py migrate --run-syncdb.