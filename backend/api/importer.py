import pandas as pd
from decimal import Decimal, InvalidOperation
from .models import FundManager, Fund


def _dec(val):
    if pd.isna(val) or val is None or val == '':
        return None
    try:
        return Decimal(str(round(float(val), 4)))
    except (InvalidOperation, ValueError):
        return None


def _int(val):
    if pd.isna(val) or val is None or val == '':
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def import_excel_file(file_obj):
    xf = pd.ExcelFile(file_obj)
    results = {'managers_created': 0, 'managers_updated': 0,
               'funds_created': 0, 'funds_updated': 0, 'errors': []}

    df = xf.parse(xf.sheet_names[0])
    df.columns = [str(c).strip() for c in df.columns]

    COL_MAP = {
        'Masked Investor Name': 'manager_name',
        'Fund Manager': 'manager_name',
        'Manager': 'manager_name',
        'Investor Name': 'manager_name',
        'Masked Fund Name': 'fund_name',
        'Fund Name': 'fund_name',
        'Fund': 'fund_name',
        'Fund ID': 'fund_id_raw',
        'Vintage': 'vintage',
        'Fund Size': 'fund_size_usd_m',
        'Fund Size (USD M)': 'fund_size_usd_m',
        'Fund Size (USD Mn)': 'fund_size_usd_m',
        'Fund Type': 'fund_type',
        'Investments': 'investments',
        'Total Investments': 'total_investments',
        'IRR': 'irr',
        'Net IRR': 'irr',
        'TVPI': 'tvpi',
        'RVPI': 'rvpi',
        'DPI': 'dpi',
        'MOIC': 'moic',
        'Fund Quartile': 'fund_quartile',
        'IRR Benchmark*': 'irr_benchmark',
        'IRR Benchmark': 'irr_benchmark',
        'TVPI Benchmark*': 'tvpi_benchmark',
        'TVPI Benchmark': 'tvpi_benchmark',
        'DPI Benchmark*': 'dpi_benchmark',
        'DPI Benchmark': 'dpi_benchmark',
        'As of Quarter': 'as_of_quarter',
        'As of Year': 'as_of_year',
        'Preferred Geography': 'geography',
        'Geography': 'geography',
        'Preferred Industry': 'sector_focus',
        'Sector Focus': 'sector_focus',
        'Strategy': 'strategy',
        'AUM (USD M)': 'aum_usd_m',
        'PB Score': 'pb_score',
        'Description': 'description',
        'Year Founded': 'year_founded',
        'Segment': 'segment',
    }

    df.rename(columns=COL_MAP, inplace=True)

    if 'manager_name' not in df.columns:
        return {'error': 'Cannot find manager column. Columns found: ' + str(list(df.columns))}

    for _, row in df.iterrows():
        manager_name = str(row.get('manager_name', '')).strip()
        fund_name = str(row.get('fund_name', '')).strip()

        if not manager_name or manager_name in ('nan', 'None', ''):
            continue

        manager, created = FundManager.objects.get_or_create(name=manager_name)
        if created:
            results['managers_created'] += 1
        else:
            results['managers_updated'] += 1

        if not fund_name or fund_name in ('nan', 'None', ''):
            continue

        fund_id_raw = str(row.get('fund_id_raw', '')).strip() or None
        if fund_id_raw in ('nan', 'None', ''):
            fund_id_raw = None

        fd = {
            'manager': manager,
            'vintage': _int(row.get('vintage')),
            'fund_size_usd_m': _dec(row.get('fund_size_usd_m')),
            'fund_type': str(row.get('fund_type', 'Buyout')).strip() or 'Buyout',
            'investments': _int(row.get('investments')),
            'irr': _dec(row.get('irr')),
            'tvpi': _dec(row.get('tvpi')),
            'rvpi': _dec(row.get('rvpi')),
            'dpi': _dec(row.get('dpi')),
            'moic': _dec(row.get('moic')),
            'fund_quartile': str(row.get('fund_quartile', '')).strip() or None,
            'irr_benchmark': _dec(row.get('irr_benchmark')),
            'tvpi_benchmark': _dec(row.get('tvpi_benchmark')),
            'dpi_benchmark': _dec(row.get('dpi_benchmark')),
            'as_of_quarter': str(row.get('as_of_quarter', '')).strip() or None,
            'as_of_year': _int(row.get('as_of_year')),
            'geography': str(row.get('geography', '')).strip() or None,
            'sector_focus': str(row.get('sector_focus', '')).strip() or None,
        }
        for k, v in list(fd.items()):
            if v in ('nan', 'None'):
                fd[k] = None

        try:
            if fund_id_raw:
                f, c = Fund.objects.update_or_create(
                    fund_id_raw=fund_id_raw,
                    defaults={'fund_name': fund_name, **fd}
                )
            else:
                f, c = Fund.objects.update_or_create(
                    fund_name=fund_name, manager=manager,
                    defaults=fd
                )
            if c:
                results['funds_created'] += 1
            else:
                results['funds_updated'] += 1
        except Exception as e:
            results['errors'].append(str(e)[:100])

    return results
