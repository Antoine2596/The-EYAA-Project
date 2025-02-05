# The-EYAA-Project

Quand on recupere le projet il faut faire :

pyhton manage.py makemigrations
python manage.py makemigrations core
python manage.py migrate
python manage.py import_my_data {Repertoire/des/donnees} {mode}
    Mode: Comportement a adopter si l id du genome existe deja : k = garde les deux, r = remplace le genome existant, i = ignore le nouveau genome 
Cela cree automatiquement les comptes suivants :

lecteur : 
    email = "lecteur@gmail.fr", 
    password = "lecteur"

annotateur :
    email = "annotateur@gmail.fr", 
    password="annotateur"

validateur:
email = "validateur@gmail.fr", 
password="validateur"

visiteur:
email = "visiteur@gmail.fr", 
password="visiteur"

admin:
email= "admin@gmail.fr", 
password="admin"

Etapes pour tracer le diagramme de classe du modele: 

pip install django-extensions

#Rajouter django_extensions dans INSTALLED_APPS de settings.py

sudo apt install graphviz
python manage.py graph_models -a --dot -o myapp_models.dot dot -Tpng myapp_models.dot -omyapp_models.png





