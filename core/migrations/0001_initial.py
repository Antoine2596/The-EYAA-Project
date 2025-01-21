# Generated by Django 5.1.5 on 2025-01-21 20:18

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genome',
            fields=[
                ('genome_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('genome_sequence', models.TextField(validators=[django.core.validators.RegexValidator(message='La séquence doit être uniquement composée des caractères ACGT ou U.', regex='^[ACGTU]*$')])),
                ('genome_type', models.CharField(choices=[('DNA', 'ADN'), ('RNA', 'ARN')], max_length=3)),
                ('organism', models.CharField(max_length=20)),
                ('is_annotated', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mot_de_passe', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('lecteur', 'Lecteur'), ('annotateur', 'Annotateur'), ('validateur', 'Validateur')], default='lecteur', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('sequence_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('dna_sequence', models.TextField()),
                ('aa_sequence', models.TextField()),
                ('num_chromosome', models.IntegerField()),
                ('sequence_start', models.IntegerField()),
                ('sequence_stop', models.IntegerField()),
                ('sequence_length', models.IntegerField()),
                ('gene_name', models.CharField(max_length=20)),
                ('sequence_status', models.CharField(choices=[('Nothing', 'Non-annotée'), ('Assigned', 'Attribuée'), ('Awaiting validation', 'En attente de validation'), ('Validated', 'Validée')], max_length=50)),
                ('genome', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sequences', to='core.genome')),
            ],
        ),
        migrations.CreateModel(
            name='Domaine',
            fields=[
                ('domain_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('domain_name', models.CharField(max_length=20)),
                ('domain_start', models.IntegerField()),
                ('domain_stop', models.IntegerField()),
                ('domain_length', models.IntegerField()),
                ('domain_function', models.CharField(max_length=50)),
                ('sequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domaines', to='core.sequence')),
            ],
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('annotation_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('annotation_text', models.TextField()),
                ('annotation_author', models.CharField(max_length=50)),
                ('sequence', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='annotation', to='core.sequence')),
            ],
        ),
    ]
