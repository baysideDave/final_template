# Generated by Django 3.1.3 on 2023-02-12 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0006_auto_20230211_0537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choice',
            name='choice_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(),
        ),
    ]