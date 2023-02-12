# Generated by Django 3.1.3 on 2023-02-11 04:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('onlinecourse', '0002_auto_20230206_0400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='lesson_id',
        ),
        migrations.AddField(
            model_name='question',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='onlinecourse.course'),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='total_learners',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.CharField(default='', max_length=1000),
        ),
    ]