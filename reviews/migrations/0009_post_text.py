# Generated by Django 4.1.7 on 2023-05-13 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_remove_postcontributor_contributor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='text',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
