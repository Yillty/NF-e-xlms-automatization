import os
import platform
import shutil
import socket
import subprocess
import time
import ctypes
import re
from pathlib import Path
from ctypes import wintypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

port = 9222
profile = Path.home() / ".sefaz_automacao_perfil"
url = 'https://plataforma.sefaz.ma.gov.br/'

selem = '/html/body/app-root/app-main/div/div[2]/div/app-download-form/p-card[1]/div/div/div[2]/form/div[2]/div/p-dropdown/div/span'
xpath_opt = "//li[contains(@class,'p-dropdown-item')]"

def popup(msg, title: str = 'Rotina XML', icon = 0x40):
    if platform.system() == 'Windows':
        ctypes.windll.user32.MessageBoxW(0, str(msg), title, icon | 0x1000)
    else:
        subprocess.run(['notify-send', title, str(msg)])


def fdoc():
    '''
    # Description
    Return path for the documents files
    '''
    if platform.system() == 'Windows':
        try:
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            if ctypes.windll.shell32.SHGetFolderPathW(None, 5,
                                                      None, 0,
                                                      buf) == 0:
                return Path(buf.value)
        except:
            pass
    else:
        cfg = Path.home() / '.config' / 'user-dirs.dirs'
        if cfg.exists():
            for line in cfg.read_text(encoding = 'utf-8').splitlines():
                if line.startswith('XDG_DOCUMENTS_DIR='):
                    path = line.split('=', 1)[1].strip().strip('"')
                    return Path(path.replace('$HOME', str(Path.home())))
    return Path.home() / 'Documentos'

def _cbrowser():
    '''
    # Description
    Returns a list of candidates for browsers to be used in the system
    '''
    sis = platform.system()
    cand = []

    if sis == 'Windows':
        bases = [os.environ.get(v) for v in
                 ('PROGRAMFILES', 'PROGRAMFILES(X86)', 'LOCALAPPDATA')]
        for base in filter(None, bases):
            cand.append(('chrome', Path(base) / 'Google/Chrome/Application/chrome.exe'))
        for base in filter(None, bases):
                    cand.append(('edge', Path(base) / 'Microsoft/Edge/Application/msedge.exe'))
    else:
          for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
                if (p := shutil.which(name)):
                      cand.append(('chrome', Path(p)))
    return cand

def _fbrowser():
    '''
    # Description
    Verifies if the browser candidates are installed 
    '''
    for kind, path in _cbrowser():
        if path.exists():
            return kind, str(path)
    raise RuntimeError('Nenhum navegador compativel... Por favor, instale Edge ou Chrome')

def _openport(port = port):
    '''
    # Description
    Opens a port in the browser for selenium access

    # Paramaters
    ## port: int, default 9222
        port to be opened.
    '''
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0

def _tab(drv, url):
    '''
    # Description
    Switch tabs to the one desired

    # Parameters
    ## drv: WebDriver 
        The driver used for the automation. <br>
    ## url: str
        Target url.
    '''
    for h in drv.window_handles:
        drv.switch_to.window(h)
        if url in drv.current_url:
            return
    drv.switch_to.window(drv.window_handles[-1])

def obrowser(profile = profile, port = port, url = url):
    '''
    # Description
    Opens Edge or Google Chrome using a port to be accessed by selenium

    # Parameters
    ## profile: Path
        user profile the browser should open on.<br> 
    ## port: int, default 9222
        port to be opened.<br>
    ## url: str
        Target url
    '''
    type, exe = _fbrowser()
    profile.mkdir(parents = True, exist_ok = True)

    if not _openport(port):
        subprocess.Popen([
            exe,
            f'--remote-debugging-port={port}',
            f'--user-data-dir={profile}',
            '--no-first-run',
            '--no-default-browser-check',
            url
        ])
        for _ in range(30):
            if _openport(port):
                break
            time.sleep(0.5)
        else:
            raise RuntimeError('O navegador não abriu a porta a tempo')

    input(
        '\nO navegador foi aberto. Faça o login e acesse a plataforma.\n'
        'Após realizado o login, retorne à esta página e aperte ENTER para continuar'
    )

    if type == 'edge':
        opt = EdgeOptions()
        opt.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
        drv = webdriver.Edge(options = opt)
    else:
        opt = ChromeOptions()
        opt.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
        drv = webdriver.Chrome(options = opt)

    _tab(drv, url)
    return drv

browser = obrowser(profile=profile, port=port, url=url)
wait = WebDriverWait(browser, timeout = 15)

def bclick(id, by: str = By.XPATH, wait = wait):
    '''
    # Description
    Clicks on the desired button

    # Parameters
    ## wait: WebDriverWait
        Wait object. It should be defined outside the function.<br>
    ## id: str 
        Value to be searched by the By. parameter.<br>
    ## by: str, default By.XPATH
        How id should be searched. Use the option of selenium.webdriver.common.by
    '''
    btt = (by, id)
    el = wait.until(EC.element_to_be_clickable(btt))
    el.click()
    return el

def _norm(t):
    '''
    # Description
    Standardizes CNPJ and firm name
    # Parameters
    ## t: str
        raw firm name as it's found.
    '''
    return re.sub(r'\s+', ' ', t).strip()

def _olist(wait = wait, selem = selem, xpath_opt = xpath_opt):
    '''
    # Description
    Opens the list of firms and wait for option to be apear
    # Parameters
    ## wait: WebDriverWait
            Wait object. It should be defined outside the function.<br>
    '''
    bclick(wait = wait, id = selem)
    wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath_opt)))

def listlist(browser = browser, wait = wait, xpath_opt = xpath_opt):
    '''
    # Description
    List firms in the selection box
    # Parameters
    ## browser: WebDriver 
            The driver used for the automation. <br>
    '''
    _olist(wait)
    itens = browser.find_elements(By.XPATH, xpath_opt)
    names = [_norm(i.get_attribute('aria-label') or i.text) for i in itens]
    browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
    return [n for n in names if n]

def select(name, wait = wait, browser = browser, xpath_opt = xpath_opt):
    '''
    # Description
    Select a firm on the selection box
    # Parameters
    ## browser: WebDriver 
            The driver used for the automation.<br>
    ## name: str
        Name of the firm to be selected
    '''
    _olist(wait)
    itens = browser.find_elements(By.XPATH, xpath_opt)
    for item in itens:
        if _norm(item.get_attribute('aria-label') or item.text) == name:
            browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
            item.click()
            return
    raise ValueError(f'Empresa não encontrada: {name}')

folder = fdoc() / 'Sefaz MA'
cache_path = folder / 'cache' / 'datas consultadas'
cache_path.parent.mkdir(parents = True, exist_ok = True)

interval = 60 * 60

