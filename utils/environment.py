"""
Detector de ambiente e configuração de driver
"""
import os
import sys
import platform


def is_running_in_docker():
    """
    Detecta se o código está rodando dentro de um container Docker/Podman
    
    :return: True se estiver em container
    """
    # Método 1: Variável de ambiente
    if os.environ.get('IN_DOCKER'):
        return True
    
    # Método 2: Verifica arquivo .dockerenv
    if os.path.exists('/.dockerenv'):
        return True
    
    # Método 3: Verifica cgroup
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'podman' in f.read()
    except:
        pass
    
    return False


def get_chromedriver_path():
    """
    Retorna o caminho correto do ChromeDriver baseado no sistema operacional
    
    :return: Caminho completo do ChromeDriver
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Se estiver em Docker ou Linux
    if is_running_in_docker():
        chromedriver_path = os.path.join(base_dir, 'utils', 'chromedriver-linux64', 'chromedriver')
        print(f"🐳 Rodando em container Docker/Podman")
        print(f"📂 ChromeDriver path: {chromedriver_path}")
        return chromedriver_path
    
    # Detecta sistema operacional
    system = platform.system().lower()
    
    if system == 'linux':
        chromedriver_path = os.path.join(base_dir, 'utils', 'chromedriver-linux64', 'chromedriver')
    elif system == 'windows':
        chromedriver_path = os.path.join(base_dir, 'utils', 'chromedriver-win64', 'chromedriver.exe')
    elif system == 'darwin':  # macOS
        chromedriver_path = os.path.join(base_dir, 'utils', 'chromedriver-mac64', 'chromedriver')
    else:
        # Default para Linux
        chromedriver_path = os.path.join(base_dir, 'utils', 'chromedriver-linux64', 'chromedriver')
    
    print(f"💻 Sistema operacional: {system}")
    print(f"📂 ChromeDriver path: {chromedriver_path}")
    
    return chromedriver_path


def get_chrome_options(headless=True):
    """
    Retorna as opções do Chrome configuradas para o ambiente
    
    :param headless: Executar em modo headless
    :return: ChromeOptions configurado
    """
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    
    # Opções comuns
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    # Opções específicas para Docker
    if is_running_in_docker():
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Define display para Xvfb
        display = os.environ.get('DISPLAY', ':99')
        print(f"🖥️  Display configurado: {display}")
    
    return chrome_options


def create_driver(headless=True):
    """
    Cria um WebDriver configurado para o ambiente correto
    
    :param headless: Executar em modo headless
    :return: WebDriver configurado
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    
    # Obtém o caminho correto do ChromeDriver
    chromedriver_path = get_chromedriver_path()
    
    # Verifica se o arquivo existe
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(
            f"ChromeDriver não encontrado em: {chromedriver_path}\n"
            f"Sistema: {platform.system()}\n"
            f"Docker: {is_running_in_docker()}"
        )
    
    # Verifica permissões de execução (Linux/Docker)
    if platform.system().lower() != 'windows':
        os.chmod(chromedriver_path, 0o755)
    
    # Configura o serviço
    service = Service(executable_path=chromedriver_path)
    
    # Obtém as opções
    options = get_chrome_options(headless=headless)
    
    # Cria o driver
    print("🚀 Inicializando ChromeDriver...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # Remove propriedades de detecção de bot
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("✅ ChromeDriver inicializado com sucesso!")
    
    return driver


def get_output_directory():
    """
    Retorna o diretório de saída correto
    Em Docker, usa /app/outputs
    Em local, usa o diretório atual
    
    :return: Caminho do diretório de saída
    """
    if is_running_in_docker():
        output_dir = '/app/outputs'
    else:
        output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Cria o diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


if __name__ == "__main__":
    # Teste do módulo
    print("=" * 60)
    print("🔧 TESTE DE DETECÇÃO DE AMBIENTE")
    print("=" * 60)
    print()
    
    print(f"Sistema Operacional: {platform.system()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Versão Python: {sys.version}")
    print(f"Docker/Podman: {'✓ SIM' if is_running_in_docker() else '✗ NÃO'}")
    print()
    
    chromedriver = get_chromedriver_path()
    print(f"ChromeDriver Path: {chromedriver}")
    print(f"ChromeDriver Existe: {'✓ SIM' if os.path.exists(chromedriver) else '✗ NÃO'}")
    print()
    
    output_dir = get_output_directory()
    print(f"Diretório de Saída: {output_dir}")
    print()
    
    print("=" * 60)
    print("Teste de criação do driver:")
    print("=" * 60)
    
    try:
        driver = create_driver(headless=True)
        driver.get("https://www.google.com")
        print(f"✓ Driver criado com sucesso!")
        print(f"✓ Título da página: {driver.title}")
        driver.quit()
    except Exception as e:
        print(f"✗ Erro ao criar driver: {e}")
