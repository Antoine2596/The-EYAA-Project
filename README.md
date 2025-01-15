# The-EYAA-Project


Compte admin créé par Anne : 

Username : admin
Password : @JlJBq4Y9eXiPX
email : anne.beigeaud2@gmail.com


Pour importer les donnees : transforme le fasta en .csv avec les bonnes categories. Ensuite on utilise la bibliotheque import export de django qui supporte les csv pour l import de donnees

En plus  cette bibliotheque permettra l export de donnees plus tard


Etapes pour tracer le diagramme de classe: 

pip install django-extensions

#Rajouter django_extensions dans INSTALLED_APPS de settings.py

sudo apt install graphviz
python manage.py graph_models -a --dot -o myapp_models.dot dot -Tpng myapp_models.dot -omyapp_models.png
