# Generated by Django 4.2.18 on 2025-02-09 17:43

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_productmodel_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productmodel',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
