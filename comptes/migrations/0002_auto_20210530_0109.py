# Generated by Django 3.2 on 2021-05-30 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comptes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='option',
            options={'ordering': ['filiere__name']},
        ),
        migrations.RenameField(
            model_name='option',
            old_name='ecole',
            new_name='filiere',
        ),
    ]