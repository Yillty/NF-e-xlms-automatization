import pandas as pd
from xml_package import *
from datetime import date
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

bclick(id = '/html/body/app-root/app-main/div/app-topbar/div/a/i')
bclick(id = '/html/body/app-root/app-main/div/div[1]/app-menu/div/ul/li/ul/li[2]/a/span')
bclick(id = '/html/body/app-root/app-main/div/div[1]/app-menu/div/ul/li/ul/li[2]/ul/li[1]/a/span')

firms = listlist()
popup(msg = f'{len(firms)} empresas encontradas')

now = date.today()
b = now.replace(day = 1)
e = now

b = b.isoformat()
e = e.isoformat()

erros = []

for i, name in enumerate(firms, 1):
    k = key(name = name, b = b, e = e)

    if not need_consulting(k, interval = interval, cache = cache_path):
        print(f'[{i}/{len(firms)}] {name}: consultado há menos de 1h. Pulando...')
        continue

    m = str(now.month)
    y = str(now.year)

    try:
        baixar(name = name, m = m, y = y)
    except Exception as erro:
        erros.append((name, repr(erro)))

erros = pd.DataFrame(erros, columns = ['firmas', 'erro'])

msg = 'Empresas que apresentaram algum erro durante a rotina:\n' + '\n'.join(erros['firmas'])

popup(msg = msg)

new = erros['firmas']
nerros = []


for firma in new:
    try:
        baixar(name = firma, m = m, y = y)
    except Exception as erro:
        nerros.append((firma, repr(erro)))

nerros = pd.DataFrame(nerros, columns = ['firmas', 'erros'])

msg = f'{len(erros['firmas']) - len(nerros['firmas'])} empresas corrigidas\n' +  'As empresas que continuaram com erro foram:\n' + '\n'.join(nerros['firmas'], sep = '\n')

popup(msg = msg)
