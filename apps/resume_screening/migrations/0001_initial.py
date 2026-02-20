# Generated migration for Resume model

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=500)),
                ('raw_text', models.TextField(blank=True)),
                ('embedding', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'resume_screening_resumes',
                'ordering': ['-created_at'],
            },
        ),
    ]
