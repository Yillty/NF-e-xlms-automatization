import time
import re
import json

def lcache(cache):
    if cache.exists():
        try:
            return json.load(cache.read_text(encoding = 'utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}

def scache(date, cache):
    tmp = cache.with_suffix('.tmp')
    tmp.write_text(json.dumps(date, ensure_ascii = False,
                              indent = 2), encoding = 'utf-8')
    tmp.replace(cache)

def key(name, b, e):
    cnpj = re.search(r'CNPJ: [\d./-]+', name).group(1)
    return f'{cnpj}|{b}|{e}'

def need_consulting(k, interval):
    last = lcache().get(k)
    return last is None or (time.time() - last) >= interval

def write_con(k):
    dates = lcache()
    dates[k] = time.time()
    scache(dates)