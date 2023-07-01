# Generated by Django 3.2.13 on 2023-06-27 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_author_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('edit_and_delete_authors_books', 'Modifier et supprimer un livre ou un auteur.'),),
            },
        ),
    ]
