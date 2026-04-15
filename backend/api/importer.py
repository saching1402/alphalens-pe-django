import pandas as pd
from decimal import Decimal, InvalidOperation
from .models import FundManager, Fund


def _dec(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return Decimal(str(round(float(val), 4)))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _int(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _str(val):
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    s = str(val).strip()
    return s if s and s not in ('nan', 'None', 'NaN') else None


def import_excel_file(file_obj):
    xf = pd.ExcelFile(file_obj)
    results = {
        'managers_created': 0, 'managers_updated': 0,
        'funds_created': 0, 'funds_updated': 0, 'errors': []
    }

    # ── Step 1: Load Consol View for manager-level data ─────────────────────
    consol_data = {}
    consol_sheet = next((s for s in xf.sheet_names if 'consol' in s.lower()), None)
    if consol_sheet:
        dc = xf.parse(consol_sheet)
        dc.columns = [str(c).strip() for c in dc.columns]
        # Map consol columns — handle "Pitchbook Mgr  Score" with double space
        CONSOL_MAP = {
            'Masked Investor Name': 'name', 'Fund Manager': 'name', 'Manager': 'name',
            'Strategy': 'strategy',
            'Pitchbook Mgr  Score': 'pb_score',   # double space
            'Pitchbook Mgr Score': 'pb_score',     # single space fallback
            'PB Score': 'pb_score',
            'AUM (USD M)': 'aum_usd_m', 'AUM': 'aum_usd_m',
            'Description': 'description',
            'Year Found': 'year_founded',           # actual column name
            'Year Founded': 'year_founded',         # fallback
            'Segment': 'segment',
            'Latest Fund Size (USD M)': 'latest_fund_size_usd_m',
        }
        dc.rename(columns=CONSOL_MAP, inplace=True)
        if 'name' in dc.columns:
            for _, row in dc.iterrows():
                name = _str(row.get('name'))
                if not name:
                    continue
                consol_data[name] = {
                    'strategy': _str(row.get('strategy')),
                    'pb_score': _dec(row.get('pb_score')),
                    'aum_usd_m': _dec(row.get('aum_usd_m')),
                    'description': _str(row.get('description')),
                    'year_founded': _int(row.get('year_founded')),
                    'segment': _str(row.get('segment')),
                    'latest_fund_size_usd_m': _dec(row.get('latest_fund_size_usd_m')),
                }

    # ── Step 2: Load Fund Manager Info sheet ────────────────────────────────
    fund_sheet = next((s for s in xf.sheet_names if 'consol' not in s.lower()), xf.sheet_names[0])
    df = xf.parse(fund_sheet)
    df.columns = [str(c).strip() for c in df.columns]

    FUND_MAP = {
        'Masked Investor Name': 'manager_name', 'Fund Manager': 'manager_name',
        'Manager': 'manager_name', 'Investor Name': 'manager_name',
        'Masked Fund Name': 'fund_name', 'Fund Name': 'fund_name', 'Fund': 'fund_name',
        'Fund ID': 'fund_id_raw',
        'Vintage': 'vintage',
        'Fund Size': 'fund_size_usd_m', 'Fund Size (USD M)': 'fund_size_usd_m',
        'Fund Type': 'fund_type',
        'Investments': 'investments',
        'Total Investments': 'total_investments',
        'IRR': 'irr', 'Net IRR': 'irr',
        'TVPI': 'tvpi', 'RVPI': 'rvpi', 'DPI': 'dpi', 'MOIC': 'moic',
        'Fund Quartile': 'fund_quartile',
        'IRR Benchmark*': 'irr_benchmark', 'IRR Benchmark': 'irr_benchmark',
        'TVPI Benchmark*': 'tvpi_benchmark', 'TVPI Benchmark': 'tvpi_benchmark',
        'DPI Benchmark*': 'dpi_benchmark', 'DPI Benchmark': 'dpi_benchmark',
        'As of Quarter': 'as_of_quarter',
        'As of Year': 'as_of_year',
        'Preferred Geography': 'geography', 'Geography': 'geography',
        'Preferred Industry': 'sector_focus', 'Sector Focus': 'sector_focus',
    }
    df.rename(columns=FUND_MAP, inplace=True)

    if 'manager_name' not in df.columns:
        return {'error': 'Cannot find manager column. Columns: ' + str(list(df.columns))}

    for _, row in df.iterrows():
        manager_name = _str(row.get('manager_name'))
        if not manager_name:
            continue

        # Build manager defaults from consol data
        mgr_defaults = {}
        if manager_name in consol_data:
            for k, v in consol_data[manager_name].items():
                if v is not None:
                    mgr_defaults[k] = v

        manager, created = FundManager.objects.get_or_create(
            name=manager_name, defaults=mgr_defaults
        )
        if not created and mgr_defaults:
            # Update manager fields from consol data
            for k, v in mgr_defaults.items():
                if v is not None:
                    setattr(manager, k, v)
            manager.save()

        if created:
            results['managers_created'] += 1
        else:
            results['managers_updated'] += 1

        fund_name = _str(row.get('fund_name'))
        if not fund_name:
            continue

        fund_id_raw = _str(row.get('fund_id_raw'))

        fd = {
            'manager': manager,
            'vintage': _int(row.get('vintage')),
            'fund_size_usd_m': _dec(row.get('fund_size_usd_m')),
            'fund_type': _str(row.get('fund_type')) or 'Buyout',
            'investments': _int(row.get('investments')),
            'total_investments': _int(row.get('total_investments')),
            'irr': _dec(row.get('irr')),
            'tvpi': _dec(row.get('tvpi')),
            'rvpi': _dec(row.get('rvpi')),
            'dpi': _dec(row.get('dpi')),
            'moic': _dec(row.get('moic')),
            'fund_quartile': _str(row.get('fund_quartile')),
            'irr_benchmark': _dec(row.get('irr_benchmark')),
            'tvpi_benchmark': _dec(row.get('tvpi_benchmark')),
            'dpi_benchmark': _dec(row.get('dpi_benchmark')),
            'as_of_quarter': _str(row.get('as_of_quarter')),
            'as_of_year': _int(row.get('as_of_year')),
            'geography': _str(row.get('geography')),
            'sector_focus': _str(row.get('sector_focus')),
        }

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
            results['errors'].append(str(e)[:150])

    return results
