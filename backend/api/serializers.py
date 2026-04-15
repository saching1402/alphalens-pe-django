from rest_framework import serializers
from .models import FundManager, Fund, Workflow, WorkflowComment


class FundSerializer(serializers.ModelSerializer):
    manager_id = serializers.UUIDField(source='manager.id', read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model = Fund
        fields = [
            'id', 'fund_id_raw', 'manager_id', 'manager_name', 'fund_name',
            'vintage', 'fund_size_usd_m', 'fund_type', 'investments',
            'total_investments', 'irr', 'tvpi', 'rvpi', 'dpi', 'moic',
            'fund_quartile', 'irr_benchmark', 'tvpi_benchmark', 'dpi_benchmark',
            'as_of_quarter', 'as_of_year', 'geography', 'sector_focus',
            'created_at', 'updated_at',
        ]


class FundWriteSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=FundManager.objects.all(), source='manager'
    )

    class Meta:
        model = Fund
        fields = [
            'id', 'fund_id_raw', 'manager_id', 'fund_name', 'vintage',
            'fund_size_usd_m', 'fund_type', 'investments', 'total_investments',
            'irr', 'tvpi', 'rvpi', 'dpi', 'moic', 'fund_quartile',
            'irr_benchmark', 'tvpi_benchmark', 'dpi_benchmark',
            'as_of_quarter', 'as_of_year', 'geography', 'sector_focus',
        ]


def _safe_avg(values):
    vals = [float(v) for v in values if v is not None]
    return round(sum(vals) / len(vals), 3) if vals else None


def _weighted_avg(nums, weights):
    pairs = [(float(n), float(w)) for n, w in zip(nums, weights)
             if n is not None and w is not None and float(w) > 0]
    if not pairs:
        return None
    total_w = sum(w for _, w in pairs)
    return round(sum(n * w for n, w in pairs) / total_w, 3) if total_w else None


def enrich_manager(manager):
    funds = list(manager.funds.all())
    irrs = [f.irr for f in funds if f.irr is not None]
    tvpis = [f.tvpi for f in funds if f.tvpi is not None]
    dpis = [f.dpi for f in funds if f.dpi is not None]
    sizes = [f.fund_size_usd_m for f in funds if f.fund_size_usd_m is not None]

    irr_benchmarks = [f.irr_benchmark for f in funds if f.irr_benchmark is not None]
    avg_irr = _safe_avg(irrs)
    avg_irr_bench = _safe_avg(irr_benchmarks)
    alpha = (round(float(avg_irr) - float(avg_irr_bench), 3)
             if avg_irr is not None and avg_irr_bench is not None else None)

    quartile_counts = {}
    for f in funds:
        if f.fund_quartile:
            q = f.fund_quartile[:1]
            quartile_counts[q] = quartile_counts.get(q, 0) + 1
    top_quartile = quartile_counts.get('1', 0)

    return {
        'id': str(manager.id),
        'name': manager.name,
        'strategy': manager.strategy,
        'pb_score': float(manager.pb_score) if manager.pb_score is not None else None,
        'aum_usd_m': float(manager.aum_usd_m) if manager.aum_usd_m is not None else None,
        'description': manager.description,
        'year_founded': manager.year_founded,
        'segment': manager.segment,
        'latest_fund_size_usd_m': float(manager.latest_fund_size_usd_m) if manager.latest_fund_size_usd_m is not None else None,
        'fund_count': len(funds),
        'avg_irr': avg_irr,
        'avg_tvpi': _safe_avg(tvpis),
        'avg_dpi': _safe_avg(dpis),
        'avg_fund_size': _safe_avg(sizes),
        'size_weighted_irr': _weighted_avg(irrs, sizes),
        'size_weighted_tvpi': _weighted_avg(tvpis, sizes),
        'top_quartile_count': top_quartile,
        'alpha_vs_benchmark': alpha,
        'created_at': manager.created_at.isoformat(),
        'updated_at': manager.updated_at.isoformat(),
        'funds': FundSerializer(funds, many=True).data,
        'workflow_status': _get_workflow_status(manager),
    }


def _get_workflow_status(manager):
    wf = manager.workflows.order_by('-updated_at').first()
    return wf.status if wf else None


class FundManagerSerializer(serializers.ModelSerializer):
    fund_count = serializers.SerializerMethodField()

    class Meta:
        model = FundManager
        fields = [
            'id', 'name', 'strategy', 'pb_score', 'aum_usd_m', 'description',
            'year_founded', 'segment', 'latest_fund_size_usd_m',
            'fund_count', 'created_at', 'updated_at',
        ]

    def get_fund_count(self, obj):
        return obj.funds.count()


class WorkflowCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowComment
        fields = ['id', 'workflow', 'author', 'body', 'created_at']
        read_only_fields = ['id', 'created_at']


class WorkflowSerializer(serializers.ModelSerializer):
    comments = WorkflowCommentSerializer(many=True, read_only=True)
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'manager', 'manager_name', 'title', 'type', 'status',
            'priority', 'description', 'comments', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
