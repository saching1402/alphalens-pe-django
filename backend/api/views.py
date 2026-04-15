from django.db.models import Avg, Count, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import FundManager, Fund, Workflow, WorkflowComment
from .serializers import (
    FundManagerSerializer, FundSerializer, FundWriteSerializer,
    WorkflowSerializer, WorkflowCommentSerializer, enrich_manager
)
from .importer import import_excel_file


# ── Health ────────────────────────────────────────────────────────────────────

@api_view(['GET'])
def health(request):
    return Response({'status': 'ok'})


# ── Fund Managers ─────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def managers_list(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        strategy = request.GET.get('strategy', '')
        qs = FundManager.objects.prefetch_related('funds', 'workflows').order_by('name')
        if search:
            qs = qs.filter(name__icontains=search)
        if strategy:
            qs = qs.filter(strategy=strategy)
        data = [enrich_manager(m) for m in qs]
        return Response(data)

    # POST — create
    ser = FundManagerSerializer(data=request.data)
    if ser.is_valid():
        mgr = ser.save()
        return Response(enrich_manager(mgr), status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def manager_detail(request, pk):
    try:
        mgr = FundManager.objects.prefetch_related('funds', 'workflows').get(pk=pk)
    except FundManager.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(enrich_manager(mgr))

    if request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        ser = FundManagerSerializer(mgr, data=request.data, partial=partial)
        if ser.is_valid():
            ser.save()
            mgr.refresh_from_db()
            mgr_refreshed = FundManager.objects.prefetch_related('funds', 'workflows').get(pk=pk)
            return Response(enrich_manager(mgr_refreshed))
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE
    mgr.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Funds ─────────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def funds_list(request):
    if request.method == 'GET':
        manager_id = request.GET.get('manager_id')
        qs = Fund.objects.select_related('manager').order_by('manager__name', 'fund_name')
        if manager_id:
            qs = qs.filter(manager_id=manager_id)
        return Response(FundSerializer(qs, many=True).data)

    ser = FundWriteSerializer(data=request.data)
    if ser.is_valid():
        fund = ser.save()
        return Response(FundSerializer(fund).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def fund_detail(request, pk):
    try:
        fund = Fund.objects.select_related('manager').get(pk=pk)
    except Fund.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(FundSerializer(fund).data)

    if request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        ser = FundWriteSerializer(fund, data=request.data, partial=partial)
        if ser.is_valid():
            fund = ser.save()
            return Response(FundSerializer(fund).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    fund.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ── Analytics ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
def analytics_dashboard(request):
    managers = FundManager.objects.prefetch_related('funds').all()
    all_irrs, all_tvpis, all_dpis = [], [], []
    top_q_count = 0

    for m in managers:
        for f in m.funds.all():
            if f.irr is not None:
                all_irrs.append(float(f.irr))
            if f.tvpi is not None:
                all_tvpis.append(float(f.tvpi))
            if f.dpi is not None:
                all_dpis.append(float(f.dpi))
            if f.fund_quartile and f.fund_quartile.startswith('1'):
                top_q_count += 1

    def avg(lst):
        return round(sum(lst) / len(lst), 3) if lst else None

    total_aum = sum(float(m.aum_usd_m) for m in managers if m.aum_usd_m)
    fund_count = Fund.objects.count()
    manager_count = managers.count()

    return Response({
        'manager_count': manager_count,
        'fund_count': fund_count,
        'total_aum_usd_m': round(total_aum, 2),
        'universe_avg_irr': avg(all_irrs),
        'universe_avg_tvpi': avg(all_tvpis),
        'universe_avg_dpi': avg(all_dpis),
        'top_quartile_count': top_q_count,
        'top_quartile_pct': round(top_q_count / fund_count * 100, 1) if fund_count else 0,
    })


@api_view(['GET'])
def analytics_scatter(request):
    x_field = request.GET.get('x', 'irr')
    y_field = request.GET.get('y', 'tvpi')
    strategy = request.GET.get('strategy', '')

    ALLOWED = {'irr', 'tvpi', 'dpi', 'rvpi', 'moic', 'fund_size_usd_m', 'pb_score', 'aum_usd_m'}
    if x_field not in ALLOWED or y_field not in ALLOWED:
        return Response({'detail': 'Invalid field'}, status=400)

    managers = FundManager.objects.prefetch_related('funds').all()
    if strategy:
        managers = managers.filter(strategy=strategy)

    result = []
    for m in managers:
        irrs = [float(f.irr) for f in m.funds.all() if f.irr is not None]
        tvpis = [float(f.tvpi) for f in m.funds.all() if f.tvpi is not None]
        dpis = [float(f.dpi) for f in m.funds.all() if f.dpi is not None]

        def get_val(field):
            if field == 'irr':
                return round(sum(irrs)/len(irrs), 3) if irrs else None
            if field == 'tvpi':
                return round(sum(tvpis)/len(tvpis), 4) if tvpis else None
            if field == 'dpi':
                return round(sum(dpis)/len(dpis), 4) if dpis else None
            if field in ('aum_usd_m', 'pb_score'):
                v = getattr(m, field)
                return float(v) if v is not None else None
            return None

        x_val = get_val(x_field)
        y_val = get_val(y_field)
        if x_val is not None and y_val is not None:
            result.append({
                'manager_id': str(m.id),
                'name': m.name,
                'strategy': m.strategy,
                'x': x_val, 'y': y_val,
                'fund_count': m.funds.count(),
                'aum': float(m.aum_usd_m) if m.aum_usd_m else None,
            })
    return Response(result)


@api_view(['GET'])
def analytics_top_managers(request):
    metric = request.GET.get('metric', 'irr')
    limit = int(request.GET.get('limit', 10))
    strategy = request.GET.get('strategy', '')

    managers = FundManager.objects.prefetch_related('funds').all()
    if strategy:
        managers = managers.filter(strategy=strategy)

    enriched = []
    for m in managers:
        funds = list(m.funds.all())
        if metric == 'irr':
            vals = [float(f.irr) for f in funds if f.irr is not None]
        elif metric == 'tvpi':
            vals = [float(f.tvpi) for f in funds if f.tvpi is not None]
        elif metric == 'dpi':
            vals = [float(f.dpi) for f in funds if f.dpi is not None]
        else:
            vals = []
        if vals:
            enriched.append({'name': m.name, 'value': round(sum(vals)/len(vals), 3), 'strategy': m.strategy})

    enriched.sort(key=lambda x: x['value'], reverse=True)
    return Response(enriched[:limit])


@api_view(['GET'])
def analytics_quartile_dist(request):
    strategy = request.GET.get('strategy', '')
    qs = Fund.objects.all()
    if strategy:
        qs = qs.filter(manager__strategy=strategy)

    dist = {'1': 0, '2': 0, '3': 0, '4': 0, 'N/A': 0}
    for f in qs:
        if f.fund_quartile:
            key = f.fund_quartile[:1]
            if key in dist:
                dist[key] = dist[key] + 1
            else:
                dist['N/A'] = dist['N/A'] + 1
        else:
            dist['N/A'] = dist['N/A'] + 1
    return Response(dist)


# ── Workflows ─────────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def workflows_list(request):
    if request.method == 'GET':
        manager_id = request.GET.get('manager_id')
        qs = Workflow.objects.select_related('manager').prefetch_related('comments')
        if manager_id:
            qs = qs.filter(manager_id=manager_id)
        return Response(WorkflowSerializer(qs, many=True).data)

    ser = WorkflowSerializer(data=request.data)
    if ser.is_valid():
        wf = ser.save()
        return Response(WorkflowSerializer(wf).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def workflow_detail(request, pk):
    try:
        wf = Workflow.objects.select_related('manager').prefetch_related('comments').get(pk=pk)
    except Workflow.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(WorkflowSerializer(wf).data)

    if request.method in ('PUT', 'PATCH'):
        partial = request.method == 'PATCH'
        ser = WorkflowSerializer(wf, data=request.data, partial=partial)
        if ser.is_valid():
            wf = ser.save()
            return Response(WorkflowSerializer(wf).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    wf.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def workflow_add_comment(request, pk):
    try:
        wf = Workflow.objects.get(pk=pk)
    except Workflow.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    data = {**request.data, 'workflow': str(wf.id)}
    ser = WorkflowCommentSerializer(data=data)
    if ser.is_valid():
        comment = ser.save()
        return Response(WorkflowCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Import ────────────────────────────────────────────────────────────────────

@api_view(['POST'])
def import_excel(request):
    if 'file' not in request.FILES:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    f = request.FILES['file']
    if not f.name.endswith(('.xlsx', '.xls')):
        return Response({'detail': 'Only .xlsx/.xls files accepted'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        result = import_excel_file(f)
        return Response(result)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
