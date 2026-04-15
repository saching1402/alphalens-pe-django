import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FundManager',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('strategy', models.CharField(blank=True, choices=[('MM', 'Mid-Market'), ('LMM', 'Lower Mid-Market')], max_length=20, null=True)),
                ('pb_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('aum_usd_m', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('year_founded', models.SmallIntegerField(blank=True, null=True)),
                ('segment', models.CharField(blank=True, max_length=100, null=True)),
                ('latest_fund_size_usd_m', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'fund_managers', 'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fund_id_raw', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='funds', to='api.fundmanager')),
                ('fund_name', models.CharField(max_length=200)),
                ('vintage', models.SmallIntegerField(blank=True, null=True)),
                ('fund_size_usd_m', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('fund_type', models.CharField(default='Buyout', max_length=100)),
                ('investments', models.IntegerField(blank=True, null=True)),
                ('irr', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('tvpi', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('rvpi', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('dpi', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('moic', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('fund_quartile', models.CharField(blank=True, max_length=80, null=True)),
                ('irr_benchmark', models.DecimalField(blank=True, decimal_places=3, max_digits=8, null=True)),
                ('tvpi_benchmark', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('dpi_benchmark', models.DecimalField(blank=True, decimal_places=4, max_digits=8, null=True)),
                ('as_of_quarter', models.CharField(blank=True, max_length=10, null=True)),
                ('as_of_year', models.SmallIntegerField(blank=True, null=True)),
                ('geography', models.CharField(blank=True, max_length=100, null=True)),
                ('sector_focus', models.CharField(blank=True, max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'funds'},
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workflows', to='api.fundmanager')),
                ('title', models.CharField(max_length=300)),
                ('type', models.CharField(choices=[('Due Diligence','Due Diligence'),('Clarification','Clarification'),('Risk Review','Risk Review'),('Performance','Performance'),('Other','Other')], default='Due Diligence', max_length=50)),
                ('status', models.CharField(choices=[('Open','Open'),('In Progress','In Progress'),('Due Diligence','Due Diligence'),('Committed','Committed'),('Declined','Declined'),('Watchlist','Watchlist'),('Resolved','Resolved'),('Closed','Closed')], default='Open', max_length=50)),
                ('priority', models.CharField(choices=[('High','High'),('Medium','Medium'),('Low','Low')], default='Medium', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'workflows', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='WorkflowComment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='api.workflow')),
                ('author', models.CharField(default='User', max_length=100)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'db_table': 'workflow_comments', 'ordering': ['created_at']},
        ),
    ]
