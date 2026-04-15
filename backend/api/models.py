import uuid
from django.db import models


class FundManager(models.Model):
    STRATEGY_CHOICES = [('MM', 'Mid-Market'), ('LMM', 'Lower Mid-Market')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, null=True, blank=True)
    pb_score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    aum_usd_m = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    year_founded = models.SmallIntegerField(null=True, blank=True)
    segment = models.CharField(max_length=200, null=True, blank=True)
    latest_fund_size_usd_m = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fund_managers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Fund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fund_id_raw = models.CharField(max_length=50, unique=True, null=True, blank=True)
    manager = models.ForeignKey(FundManager, on_delete=models.CASCADE, related_name='funds')
    fund_name = models.CharField(max_length=200)
    vintage = models.SmallIntegerField(null=True, blank=True)
    fund_size_usd_m = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fund_type = models.CharField(max_length=100, default='Buyout')
    investments = models.IntegerField(null=True, blank=True)
    total_investments = models.IntegerField(null=True, blank=True)
    irr = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    tvpi = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    rvpi = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    dpi = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    moic = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    fund_quartile = models.CharField(max_length=80, null=True, blank=True)
    irr_benchmark = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    tvpi_benchmark = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    dpi_benchmark = models.DecimalField(max_digits=8, decimal_places=4, null=True, blank=True)
    as_of_quarter = models.CharField(max_length=10, null=True, blank=True)
    as_of_year = models.SmallIntegerField(null=True, blank=True)
    geography = models.CharField(max_length=300, null=True, blank=True)
    sector_focus = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funds'
        ordering = ['manager__name', 'fund_name']

    def __str__(self):
        return self.fund_name


class Workflow(models.Model):
    STATUS_CHOICES = [
        ('Due Diligence', 'Due Diligence'), ('Committed', 'Committed'),
        ('Declined', 'Declined'), ('Watchlist', 'Watchlist'),
        ('Open', 'Open'), ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'), ('Closed', 'Closed'),
    ]
    TYPE_CHOICES = [
        ('Due Diligence', 'Due Diligence'), ('Clarification', 'Clarification'),
        ('Risk Review', 'Risk Review'), ('Performance', 'Performance'), ('Other', 'Other'),
    ]
    PRIORITY_CHOICES = [('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    manager = models.ForeignKey(FundManager, on_delete=models.CASCADE, related_name='workflows')
    title = models.CharField(max_length=300)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Due Diligence')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workflows'
        ordering = ['-created_at']


class WorkflowComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=100, default='User')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow_comments'
        ordering = ['created_at']
