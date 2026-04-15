from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        # Add total_investments to Fund
        migrations.AddField(
            model_name='fund',
            name='total_investments',
            field=models.IntegerField(blank=True, null=True),
        ),
        # Expand geography field
        migrations.AlterField(
            model_name='fund',
            name='geography',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        # Expand sector_focus field
        migrations.AlterField(
            model_name='fund',
            name='sector_focus',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        # Expand segment field on FundManager
        migrations.AlterField(
            model_name='fundmanager',
            name='segment',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        # Expand pb_score precision
        migrations.AlterField(
            model_name='fundmanager',
            name='pb_score',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True),
        ),
    ]
