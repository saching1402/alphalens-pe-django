"""
Excel importer — reads the PE fund manager workbook and upserts into DB.
Expected sheets:
  - Sheet with fund-level data (IRR, TVPI, DPI, etc.)
  - 'Consol View' tab with manager-level AUM, description, PB score
"""
import pandas as pd
from decimal import Decimal, InvalidOperation
from .models import FundManager, Fund


def _dec(val):
    if pd.isna(val) or val is None or val == '':
        return None
    try:
        return Decimal(str(val)).quantize(Decimal('0.001'))
    except InvalidOperation:
        return None


def _int(val):
    if pd.isna(val) or val is None or val == '':
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def import_excel_file(file_obj):
    xf = pd.ExcelFile(file_obj)
    sheets = xf.sheet_names
    results = {'managers_created': 0, 'managers_updated': 0,
               'funds_created': 0, 'funds_updated': 0, 'errors': []}

    # Try to find fund sheet (not Consol View)
    fund_sheet = next((s for s in sheets if 'consol' not in s.lower()), sheets[0])
    df_funds = xf.parse(fund_sheet)
    df_funds.columns = [str(c).strip() for c in df_funds.columns]

    # Column name mappings (flexible)
    COL_MAP = {
        'Fund Manager': 'manager_name',
        'Manager': 'manager_name',
        'Fund Name': 'fund_name',
        'Fund': 'fund_name',
        'Vintage': 'vintage',
        'Fund Size (USD M)': 'fund_size_usd_m',
        'Fund Size': 'fund_size_usd_m',
        'IRR (%)': 'irr',
        'IRR': 'irr',
        'Net IRR': 'irr',
        'TVPI': 'tvpi',
        'DPI': 'dpi',
        'RVPI': 'rvpi',
        'MOIC': 'moic',
        'Fund Quartile': 'fund_quartile',
        'Quartile': 'fund_quartile',
        'IRR Benchmark': 'irr_benchmark',
        'Benchmark IRR': 'irr_benchmark',
        'TVPI Benchmark': 'tvpi_benchmark',
        'DPI Benchmark': 'dpi_benchmark',
        'Strategy': 'strategy',
        'Fund Type': 'fund_type',
        'Geography': 'geography',
        'Sector Focus': 'sector_focus',
        'No. of Investments': 'investments',
        'Investments': 'investments',
    }

    df_funds.rename(columns=COL_MAP, inplace=True)

    for _, row in df_funds.iterrows():
        manager_name = str(row.get('manager_name', '')).strip()
        fund_name = str(row.get('fund_name', '')).strip()
        if not manager_name or not fund_name or manager_name == 'nan':
            continue

        strategy = str(row.get('strategy', '')).strip() or None
        if strategy and strategy not in ('MM', 'LMM'):
            strategy = None

        manager, created = FundManager.objects.get_or_create(
            name=manager_name,
            defaults={'strategy': strategy}
        )
        if created:
            results['managers_created'] += 1
        else:
            results['managers_updated'] += 1

        fund_id_raw = str(row.get('fund_id_raw', '')).strip() or None
        fund_defaults = {
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
            'geography': str(row.get('geography', '')).strip() or None,
            'sector_focus': str(row.get('sector_focus', '')).strip() or None,
        }

        if fund_id_raw:
            fund, f_created = Fund.objects.update_or_create(
                fund_id_raw=fund_id_raw,
                defaults={'fund_name': fund_name, **fund_defaults}
            )
        else:
            fund, f_created = Fund.objects.update_or_create(
                fund_name=fund_name, manager=manager,
                defaults=fund_defaults
            )

        if f_created:
            results['funds_created'] += 1
        else:
            results['funds_updated'] += 1

    # Consol View — update manager-level fields
    if 'Consol View' in sheets:
        df_consol = xf.parse('Consol View')
        df_consol.columns = [str(c).strip() for c in df_consol.columns]
        CONSOL_MAP = {
            'Fund Manager': 'name', 'Manager': 'name',
            'AUM (USD M)': 'aum_usd_m', 'AUM': 'aum_usd_m',
            'PB Score': 'pb_score', 'Description': 'description',
            'Year Founded': 'year_founded', 'Segment': 'segment',
        }
        df_consol.rename(columns=CONSOL_MAP, inplace=True)
        for _, row in df_consol.iterrows():
            name = str(row.get('name', '')).strip()
            if not name or name == 'nan':
                continue
            updates = {}
            if 'aum_usd_m' in df_consol.columns:
                updates['aum_usd_m'] = _dec(row.get('aum_usd_m'))
            if 'pb_score' in df_consol.columns:
                updates['pb_score'] = _dec(row.get('pb_score'))
            if 'description' in df_consol.columns:
                desc = str(row.get('description', '')).strip()
                if desc and desc != 'nan':
                    updates['description'] = desc
            if 'year_founded' in df_consol.columns:
                updates['year_founded'] = _int(row.get('year_founded'))
            if updates:
                FundManager.objects.filter(name=name).update(**updates)

    return results
