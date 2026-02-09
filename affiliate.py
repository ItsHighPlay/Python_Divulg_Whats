"""
Módulo para gerenciar links de afiliado do Mercado Livre
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.support import wait_for_element
from utils.environment import create_driver, get_output_directory
from utils.email_handler import EmailHandler, load_email_credentials


def load_account_credentials(file_path='account.txt'):
    """
    Carrega as credenciais do arquivo account.txt
    
    :param file_path: Caminho do arquivo de credenciais
    :return: Tupla (login, password)
    """
    credentials = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    credentials[key.strip()] = value.strip()
        
        login = credentials.get('login', '')
        password = credentials.get('password', '')
        
        if not login or not password:
            raise ValueError("Credenciais vazias no arquivo account.txt")
        
        return login, password
    except FileNotFoundError:
        raise FileNotFoundError("Arquivo account.txt não encontrado")
    except Exception as e:
        raise Exception(f"Erro ao ler credenciais: {str(e)}")


def login_mercado_livre(driver: WebDriver, email: str, password: str, handle_2fa: bool = True):
    """
    Realiza login no Mercado Livre com suporte a verificação 2FA por e-mail
    
    :param driver: WebDriver do Selenium
    :param email: Email de login
    :param password: Senha
    :param handle_2fa: Se deve tentar automatizar verificação 2FA
    :return: True se login bem-sucedido
    """
    try:
        print("Acessando página de login...")
        driver.get("https://www.mercadolivre.com.br/")
        time.sleep(2)
        
        # Procura e clica no botão de login
        login_button = wait_for_element(driver, (By.CSS_SELECTOR, 'a[data-link-id="login"]'), seconds=10)
        if login_button:
            login_button.click()
            time.sleep(2)
        
        # Preenche email
        print("Preenchendo email...")
        email_field = wait_for_element(driver, (By.ID, 'user_id'), seconds=10)
        if email_field:
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1)
            
            # Clica em continuar
            continue_button = driver.find_element(By.ID, 'continue_button')
            continue_button.click()
            time.sleep(2)
        
        # Preenche senha
        print("Preenchendo senha...")
        password_field = wait_for_element(driver, (By.ID, 'password'), seconds=10)
        if password_field:
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Clica em entrar
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            time.sleep(3)
        
        # Verifica se há solicitação de código de verificação
        if handle_2fa and _check_verification_code_required(driver):
            print("\n⚠️  Código de verificação solicitado!")
            
            # Tenta obter código por e-mail automaticamente
            if _handle_email_verification(driver):
                print("✓ Verificação 2FA concluída com sucesso!")
            else:
                print("⚠️  Não foi possível obter código automaticamente")
                print("Digite o código manualmente ou aguarde timeout")
                
                # Aguarda entrada manual (60 segundos)
                time.sleep(60)
        
        print("Login realizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao fazer login: {str(e)}")
        return False


def _check_verification_code_required(driver: WebDriver, timeout: int = 5):
    """
    Verifica se há solicitação de código de verificação
    
    :param driver: WebDriver
    :param timeout: Timeout em segundos
    :return: True se código for solicitado
    """
    try:
        # Possíveis indicadores de página de verificação
        verification_indicators = [
            (By.ID, 'verification-code'),
            (By.ID, 'code'),
            (By.NAME, 'code'),
            (By.CSS_SELECTOR, 'input[placeholder*="código"]'),
            (By.CSS_SELECTOR, 'input[placeholder*="codigo"]'),
            (By.CSS_SELECTOR, 'input[placeholder*="verification"]'),
            (By.XPATH, '//*[contains(text(), "código de verificação")]'),
            (By.XPATH, '//*[contains(text(), "codigo de verificacao")]'),
        ]
        
        for locator in verification_indicators:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located(locator)
                )
                if element:
                    print(f"   Detectado campo de verificação: {locator}")
                    return True
            except TimeoutException:
                continue
        
        return False
        
    except Exception as e:
        print(f"Erro ao verificar código: {str(e)}")
        return False


def _handle_email_verification(driver: WebDriver):
    """
    Tenta obter código de verificação por e-mail e preencher automaticamente
    
    :param driver: WebDriver
    :return: True se código foi inserido com sucesso
    """
    try:
        # Carrega credenciais de e-mail
        email_addr, email_pass = load_email_credentials()
        
        if not email_addr or not email_pass:
            print("⚠️  Credenciais de e-mail não configuradas")
            print("   Adicione ao account.txt:")
            print("   email = seu_email@gmail.com")
            print("   email_password = sua_senha_de_app")
            return False
        
        print(f"\n📧 Conectando ao e-mail: {email_addr}")
        
        # Cria handler de e-mail
        email_handler = EmailHandler(email_addr, email_pass)
        
        if not email_handler.connect():
            print("✗ Não foi possível conectar ao e-mail")
            return False
        
        # Verifica se há opção de enviar código por e-mail
        _request_code_by_email(driver)
        
        # Busca código no e-mail
        verification_code = email_handler.get_verification_code_from_mercadolivre(
            max_attempts=12,  # 12 tentativas (1 minuto)
            wait_seconds=5
        )
        
        email_handler.disconnect()
        
        if not verification_code:
            print("✗ Código não encontrado no e-mail")
            return False
        
        # Verifica credenciais de e-mail
        from utils.email_handler import load_email_credentials
        email_addr, email_pass = load_email_credentials()
        if email_addr and email_pass:
            print(f"E-mail configurado para 2FA: {email_addr[:3]}***@***")
        else:
            print("⚠️  E-mail não configurado (verificação 2FA manual se necessário)")
        
        # Cria driver
        driver = create_affiliate_driver(headless=False)
        
        # Faz login (com suporte a 2FA)
        if login_mercado_livre(driver, email, senha, handle_2fa=True
            time.sleep(2)
            
            # Clica no botão de confirmar
            if _submit_verification_code(driver):
                print("✓ Código confirmado!")
                time.sleep(3)
                return True
        
        return False
        
    except Exception as e:
        print(f"Erro ao processar verificação por e-mail: {str(e)}")
        return False


def _request_code_by_email(driver: WebDriver):
    """
    Tenta clicar na opção de enviar código por e-mail
    
    :param driver: WebDriver
    """
    try:
        # Possíveis textos de botões para enviar por e-mail
        email_button_texts = [
            "Enviar código por e-mail",
            "Enviar por e-mail",
            "E-mail",
            "Email",
            "Receber por e-mail",
        ]
        
        for text in email_button_texts:
            try:
                button = driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
                if button:
                    print(f"   Clicando em: {text}")
                    button.click()
                    time.sleep(2)
                    return
            except NoSuchElementException:
                continue
        
        print("   ℹ️  Botão de e-mail não encontrado (pode já estar selecionado)")
        
    except Exception as e:
        print(f"   Erro ao solicitar código por e-mail: {str(e)}")


def _insert_verification_code(driver: WebDriver, code: str):
    """
    Insere código de verificação no campo
    
    :param driver: WebDriver
    :param code: Código a inserir
    :return: True se inserido com sucesso
    """
    try:
        # Possíveis localizadores do campo de código
        code_field_locators = [
            (By.ID, 'verification-code'),
            (By.ID, 'code'),
            (By.NAME, 'code'),
            (By.CSS_SELECTOR, 'input[type="tel"]'),
            (By.CSS_SELECTOR, 'input[type="text"][maxlength="6"]'),
            (By.CSS_SELECTOR, 'input[placeholder*="código"]'),
            (By.CSS_SELECTOR, 'input[placeholder*="codigo"]'),
            (By.XPATH, '//input[@type="text" or @type="tel"]'),
        ]
        
        for locator in code_field_locators:
            try:
                field = driver.find_element(*locator)
                if field and field.is_displayed():
                    field.clear()
                    field.send_keys(code)
                    print(f"   ✓ Código inserido no campo: {locator}")
                    return True
            except NoSuchElementException:
                continue
        
        print("   ✗ Campo de código não encontrado")
        return False
        
    except Exception as e:
        print(f"   Erro ao inserir código: {str(e)}")
        return False


def _submit_verification_code(driver: WebDriver):
    """
    Clica no botão de confirmar código
    
    :param driver: WebDriver
    :return: True se clicado com sucesso
    """
    try:
        # Possíveis localizadores do botão de confirmar
        submit_button_locators = [
            (By.CSS_SELECTOR, 'button[type="submit"]'),
            (By.XPATH, '//button[contains(text(), "Confirmar")]'),
            (By.XPATH, '//button[contains(text(), "Verificar")]'),
            (By.XPATH, '//button[contains(text(), "Continuar")]'),
            (By.ID, 'submit-button'),
            (By.CSS_SELECTOR, 'button.andes-button--large'),
        ]
        
        for locator in submit_button_locators:
            try:
                button = driver.find_element(*locator)
                if button and button.is_displayed() and button.is_enabled():
                    button.click()
                    print(f"   ✓ Botão de confirmação clicado: {locator}")
                    return True
            except NoSuchElementException:
                continue
        
        print("   ⚠️  Botão de confirmação não encontrado")
        return False
        
    except Exception as e:
        print(f"   Erro ao clicar em confirmar: {str(e)}")
        return False


def generate_affiliate_links(driver: WebDriver, product_urls: list, headless=False):
    """
    Gera links de afiliado para uma lista de URLs de produtos
    
    :param driver: WebDriver do Selenium
    :param product_urls: Lista de URLs de produtos
    :param headless: Executar em modo headless
    :return: Lista de links de afiliado gerados
    """
    affiliate_links = []
    
    try:
        print(f"\nGerando links de afiliado para {len(product_urls)} produtos...")
        
        # Acessa a página de link builder
        driver.get("https://www.mercadolivre.com.br/afiliados/linkbuilder#hub")
        time.sleep(3)
        
        # Aguarda o campo de textarea ficar disponível
        textarea = wait_for_element(
            driver, 
            (By.CSS_SELECTOR, 'textarea[id^="url-"]'),
            seconds=15
        )
        
        if not textarea:
            print("Erro: Campo de URL não encontrado")
            return affiliate_links
        
        # Processa URLs em lotes de 10 (limite do Mercado Livre)
        batch_size = 10
        for i in range(0, len(product_urls), batch_size):
            batch = product_urls[i:i+batch_size]
            
            print(f"Processando lote {i//batch_size + 1} ({len(batch)} URLs)...")
            
            # Limpa o campo
            textarea.clear()
            time.sleep(0.5)
            
            # Insere as URLs separadas por linha
            urls_text = '\n'.join(batch)
            textarea.send_keys(urls_text)
            time.sleep(2)
            
            # Aguarda os links serem gerados
            try:
                # Aguarda o campo de resultado aparecer
                result_textarea = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea[id^="textfield-copyLink"]'))
                )
                time.sleep(1)
                
                # Captura os links gerados
                generated_links = result_textarea.get_attribute('value')
                if generated_links:
                    # Separa os links por linha
                    links = [link.strip() for link in generated_links.split('\n') if link.strip()]
                    affiliate_links.extend(links)
                    print(f"✓ {len(links)} links de afiliado gerados neste lote")
                
            except Exception as e:
                print(f"Erro ao capturar links do lote: {str(e)}")
            
            # Aguarda antes de processar o próximo lote
            if i + batch_size < len(product_urls):
                time.sleep(2)
        
        print(f"\n✓ Total de {len(affiliate_links)} links de afiliado gerados com sucesso!")
        return affiliate_links
        
    except Exception as e:
        print(f"Erro ao gerar links de afiliado: {str(e)}")
        return affiliate_links


def create_affiliate_driver(headless=True):
    """
    Cria um driver configurado para operações de afiliados
    Usa detecção automática de ambiente (Linux/Windows/Docker)
    
    :param headless: Executar em modo headless
    :return: WebDriver configurado
    """
    return create_driver(headless=headless)


if __name__ == "__main__":
    # Teste do módulo
    try:
        print("=== Teste do Módulo de Afiliados ===\n")
        
        # Carrega credenciais
        email, senha = load_account_credentials()
        print(f"Credenciais carregadas: {email[:3]}***")
        
        # Cria driver
        driver = create_affiliate_driver(headless=False)
        
        # Faz login
        if login_mercado_livre(driver, email, senha):
            # URLs de teste
            test_urls = [
                "https://www.mercadolivre.com.br/apple-iphone-13-128-gb-meia-noite-distribuidor-autorizado/p/MLB18830478"
            ]
            
            # Gera links
            links = generate_affiliate_links(driver, test_urls)
            
            print("\n=== Links Gerados ===")
            for idx, link in enumerate(links, 1):
                print(f"{idx}. {link}")
        
        driver.quit()
        
    except Exception as e:
        print(f"Erro no teste: {str(e)}")
