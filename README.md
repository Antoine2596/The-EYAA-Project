
![ezgif-32bcf867cfbca3](https://github.com/user-attachments/assets/f2690f4a-3fc4-47c6-9cd0-7bf5afccf02e)


# The-EYAA-Project  

The EYAA Project est une application web permettant de gérer l'annotation et la visualisation de génomes procaryotes.  

Un diagramme UML de la base de données est disponible : **models_diagram.png**.

---

## 🚀 Installation  

Pour installer ce projet, suivez les étapes ci-dessous :  

### 1️⃣ Cloner le repository  

```bash
git clone git@github.com:Antoine2596/The-EYAA-Project.git
cd ./The-EYAA-Project
```

### 2️⃣ Installer les dépendances  

```bash
pip install -r requirements.txt
```

---

## 🔧 Utilisation  

Une fois installé, utilisez le projet en suivant ces étapes dans le répertoire du projet :  

### 1️⃣ Créer la base de données  

```bash
python manage.py makemigrations
python manage.py makemigrations core
python manage.py migrate
```

### 2️⃣ Importer les données  

```bash
python manage.py import_my_data {Repertoire/des/donnees} {mode}
```

📌 **Modes d'importation** :  
- `k` → Garde les deux génomes
- `r` → Remplace le génome existant
- `i` → Ignore le nouveau génome

### 3️⃣ Lancer le serveur en local  

```bash
python manage.py runserver
```

### ⚙️ Automatiser la migration et l'importation des données

Un script bash **run_django_migrations.sh** est disponible pour faciliter ces actions. 

#### Utilisation :
```bash
./run_django_migrations.sh <Repertoire/des/donnees> <mode>
```


---

## 🎯 Fonctionnalités  

Cette application propose plusieurs rôles utilisateurs avec des accès spécifiques :  

### 🔹 Visiteur  
🅿️ **Rôle temporaire** en attendant la validation du compte par un administrateur. Il ne peut rien faire sur l'application.  

### 🔹 Lecteur  
✅ Peut effectuer des requêtes sur la base de données et exporter les résultats.  
✅ Peut visualiser les génomes, les séquences et les annotations.  

### 🔹 Annotateur  
✅ A les mêmes droits que le lecteur.  
✅ Peut annoter des séquences qui lui sont attribuées.  
✅ Utilise les bases de données **InterPro** et **UniProt** pour l’annotation.  

### 🔹 Validateur  
✅ A les mêmes droits que l’annotateur.  
✅ Peut **valider** ou **refuser** les annotations soumises.  
✅ Peut attribuer des séquences à annoter **manuellement ou automatiquement**.  

### 🔹 Administrateur  
🔧 **Possède tous les droits** sur la base de données et gère la validation des comptes utilisateurs.  

---

## 🔑 Comptes par défaut  

Lors de l'importation des données, les comptes suivants sont créés automatiquement :  

| 🏷️ Rôle         | 📧 Email                | 🔐 Mot de passe  |
|----------------|------------------------|----------------|
| **Visiteur**   | visiteur@gmail.fr      | visiteur       |
| **Lecteur**    | lecteur@gmail.fr       | lecteur        |
| **Annotateur** | annotateur@gmail.fr    | annotateur     |
| **Validateur** | validateur@gmail.fr    | validateur     |
| **Admin**      | admin@gmail.fr         | admin          |

---

## ✨ Auteurs  

- **Youna Maillié** - [GitHub](https://github.com/YounaMKr)  
- **Antoine Loth** - [GitHub](https://github.com/Antoine2596)  
- **Anne Beigeaud** - [GitHub](https://github.com/abgd29)  
- **Emma Le Roy Pardonche**  - [GitHub](https://github.com/emmaleroyp)  

---



