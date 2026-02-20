# Generated migration for extracted_skills and indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume_screening', '0002_jobposting'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='extracted_skills',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='resume',
            index=models.Index(fields=['created_at'], name='resume_resume_created_idx'),
        ),
        migrations.AddIndex(
            model_name='jobposting',
            index=models.Index(fields=['created_at'], name='resume_job_created_idx'),
        ),
    ]
