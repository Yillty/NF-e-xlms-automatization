import time
import re
import json

def lcache(cache):
    '''
    # Description
    Read the script cache
    # Parameters
    ## cache: path
        Cache path
    '''
    if cache.exists():
        try:
            return json.load(cache.read_text(encoding = 'utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}

def scache(date, cache):
    '''
    # Description
    Saves cache
    # Parameters
    ## date: str
        date when last consultation was made
    ## cache: path
        Cache path
    '''
    tmp = cache.with_suffix('.tmp')
    tmp.write_text(json.dumps(date, ensure_ascii = False,
                              indent = 2), encoding = 'utf-8')
    tmp.replace(cache)

def key(name, b, e):
    '''
    # Description
    Creates a key containing firm CNPJ, beggining date and end data
    
    '''
    m = re.search(r'CNPJ:\s*([\d./-]+)', name)
    if m is None:
        raise ValueError(f'CNPJ não encontrado em {name!r}')
    cnpj = m.group(1)
    return f'{cnpj}|{b}|{e}'

def need_consulting(k, interval, cache):
    last = lcache(cache).get(k)
    return last is None or (time.time() - last) >= interval

def write_con(k, cache):
    dates = lcache(cache)
    dates[k] = time.time()
    scache(dates)