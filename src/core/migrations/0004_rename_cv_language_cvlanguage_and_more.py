# Generated by Django 4.2.4 on 2023-08-16 16:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_userskill_options_remove_userskill_level'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CV_Language',
            new_name='CVLanguage',
        ),
        migrations.RemoveField(
            model_name='project',
            name='is_completed',
        ),
    ]
