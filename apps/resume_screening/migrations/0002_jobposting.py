# Generated migration for JobPosting model

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_screening', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('embedding', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'resume_screening_job_postings',
                'ordering': ['-created_at'],
            },
        ),
    ]
