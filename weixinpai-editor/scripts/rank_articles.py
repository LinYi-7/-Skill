#!/usr/bin/env python3
"""Rank supplied article metrics without confusing unknown or censored counts."""
import argparse, csv, json, re
from decimal import Decimal
from pathlib import Path

MISSING = {'', 'na', 'n/a', 'null', 'none', '未知', '缺失', '--'}

def count_value(value):
    if value is None: return ('missing', None)
    if isinstance(value, bool): return ('invalid', None)
    text = str(value).strip().lower().replace(',', '').replace('，', '').replace(' ', '')
    if text in MISSING: return ('missing', None)
    match = re.fullmatch(r'(\d+(?:\.\d+)?)(万|w)?(\+)?', text)
    if not match: return ('invalid', None)
    number = Decimal(match[1]) * (10000 if match[2] else 1)
    if number != number.to_integral_value(): return ('invalid', None)
    return ('lower_bound' if match[3] else 'exact', int(number))

def clean(value):
    return '' if value is None else str(value).strip()

def rank(records):
    if not isinstance(records, list): raise ValueError('Input must be an array of records')
    groups, excluded, duplicates = {}, [], []
    seen = set()
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict): raise ValueError(f'Record {index} must be an object')
        item = dict(record, input_row=index)
        status, value = count_value(record.get('reads'))
        item.update(read_status=status, read_number=value)
        required = ['article_id','title','platform','account','metric','window_hours','observed_at','data_source']
        missing = [k for k in required if not clean(record.get(k))]
        if missing:
            item['exclusion_reason'] = 'Missing comparable metadata: ' + ', '.join(missing)
            excluded.append(item); continue
        window = clean(record['window_hours']).lower()
        if window != 'cumulative':
            try:
                w = Decimal(window)
                if not w.is_finite() or w <= 0: raise ValueError()
                window = format(w.normalize(), 'f')
            except Exception:
                item['exclusion_reason'] = 'window_hours must be positive hours or cumulative'
                excluded.append(item); continue
        key = tuple(clean(record.get(k)) for k in ['platform','account','metric']) + (window,clean(record.get('cohort')))
        identity = key + (clean(record['article_id']),)
        if identity in seen:
            duplicates.append(item)
            # Ambiguous observations must not arbitrarily win a ranking.
            previous = groups[key]
            for bucket in ['exact','lower_bound','missing','invalid']:
                moved = [x for x in previous[bucket] if clean(x['article_id']) == identity[-1]]
                for old in moved:
                    previous[bucket].remove(old)
                    duplicates.append(old)
            continue
        seen.add(identity)
        group = groups.setdefault(key, {'platform':key[0], 'account':key[1], 'metric':key[2], 'window_hours':window, 'cohort':key[4], 'exact':[], 'lower_bound':[], 'missing':[], 'invalid':[]})
        group[status].append(item)
    for group in groups.values():
        group['exact'].sort(key=lambda r: (-r['read_number'], r['input_row']))
        last = None
        rank_number = 0
        for pos, item in enumerate(group['exact'], 1):
            if item['read_number'] != last: rank_number = pos
            item['rank'] = rank_number
            last = item['read_number']
        # Bounds are deliberately unranked; a larger bound need not mean larger actual reads.
    return {'input_count':len(records),'groups':list(groups.values()),'excluded':excluded,'duplicate_observations':duplicates,
            'notes':['Only exact counts have ranks; equal counts retain equal rank.',
                     'Lower bounds, missing counts and invalid values are not exact ranks.',
                     'Cumulative counts are age-confounded; observed_at values and cohorts need human review.',
                     'Duplicate article observations within a comparison group are isolated; select the intended observation before rerunning.',
                     'This output does not establish causality or content quality.']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input'); parser.add_argument('output')
    args=parser.parse_args()
    source=Path(args.input)
    if source.suffix.lower()=='.csv':
        with source.open(encoding='utf-8-sig',newline='') as f: records=list(csv.DictReader(f))
    else: records=json.loads(source.read_text(encoding='utf-8-sig'))
    result=rank(records)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Processed {result['input_count']} records into {len(result['groups'])} groups")

if __name__=='__main__': main()
