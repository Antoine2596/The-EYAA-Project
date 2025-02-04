<!-- import_form.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Importer des génomes</title>
</head>
<body>
    <h1>Importer un fichier FASTA</h1>

    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Importer</button>
    </form>
</body>
</html>
