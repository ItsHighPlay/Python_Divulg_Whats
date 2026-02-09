"""
Script de teste rápido para verificar se tudo está funcionando
"""
import os
import sys


def test_environment():
    """Testa informações do ambiente"""
    print("🧪 Testando ambiente...")
    
    import platform
    from utils.environment import is_running_in_docker, get_chromedriver_path, get_output_directory
    
    print(f"✓ Sistema: {platform.system()} {platform.release()}")
    print(f"✓ Python: {sys.version.split()[0]}")
    print(f"✓ Arquitetura: {platform.machine()}")
    print(f"✓ Docker/Podman: {'SIM' if is_running_in_docker() else 'NÃO'}")
    
    driver_path = get_chromedriver_path()
    print(f"✓ ChromeDriver: {driver_path}")
    print(f"✓ ChromeDriver existe: {'SIM' if os.path.exists(driver_path) else 'NÃO'}")
    
    output_dir = get_output_directory()
    print(f"✓ Output dir: {output_dir}")
    print()


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    
    try:
        import selenium
        print(f"✓ Selenium {selenium.__version__}")
    except ImportError as e:
        print(f"✗ Selenium: {e}")
        return False
    
    try:
        import xlsxwriter
        print("✓ XlsxWriter OK")
    except ImportError as e:
        print(f"✗ XlsxWriter: {e}")
        return False
    
    try:
        import pywhatkit
        print("✓ PyWhatKit OK")
    except ImportError as e:
        print(f"✗ PyWhatKit: {e}")
        return False
    
    try:
        import art
        print("✓ Art OK")
    except ImportError as e:
        print(f"✗ Art: {e}")
        return False
    
    try:
        from utils.support import wait_for_element
        print("✓ Utils.support OK")
    except ImportError as e:
        print(f"✗ Utils.support: {e}")
        return False
    
    try:
        from utils.environment import create_driver
        print("✓ Utils.environment OK")
    except ImportError as e:
        print(f"✗ Utils.environment: {e}")
        return False
    
    print()
    return True


def test_account_file():
    """Testa se o arquivo de credenciais existe e está configurado"""
    print("🧪 Testando arquivo de credenciais...")
    
    try:
        with open('account.txt', 'r') as f:
            content = f.read()
            
            if 'login = ' in content and 'password = ' in content:
                lines = content.strip().split('\n')
                login_line = [l for l in lines if l.startswith('login')][0]
                pass_line = [l for l in lines if l.startswith('password')][0]
                
                login = login_line.split('=')[1].strip()
                password = pass_line.split('=')[1].strip()
                
                if login and password and login != "seu_email@exemplo.com":
                    print(f"✓ Credenciais ML configuradas: {login[:3]}***")
                else:
                    print("⚠️  Credenciais ML vazias ou padrão - edite account.txt")
                
                # Verifica credenciais de e-mail (opcional para 2FA)
                if 'email = ' in content and 'email_password = ' in content:
                    email_line = [l for l in lines if l.startswith('email') and not l.startswith('email_password')][0]
                    email = email_line.split('=')[1].strip()
                    
                    if email and email != "seu_email@gmail.com":
                        print(f"✓ E-mail para 2FA configurado: {email[:3]}***@***")
                        print("  📧 Verificação 2FA automática habilitada")
                    else:
                        print("⚠️  E-mail para 2FA não configurado (2FA será manual)")
                        print("  💡 Veja EMAIL_2FA_SETUP.md para configurar")
                else:
                    print("ℹ️  E-mail para 2FA não configurado (opcional)")
                    print("  💡 Para automatizar 2FA, veja EMAIL_2FA_SETUP.md")
            else:
                print("✗ Formato incorreto do account.txt")
                return False
                
    except FileNotFoundError:
        print("✗ Arquivo account.txt não encontrado")
        print("   Crie o arquivo baseado em account.txt.example")
        return False
    
    print()
    return True


def test_modules():
    """Testa se os módulos customizados funcionam"""
    print("🧪 Testando módulos customizados...")
    
    try:
        from affiliate import load_account_credentials
        print("✓ Módulo affiliate.py OK")
    except Exception as e:
        print(f"✗ affiliate.py: {e}")
        return False
    
    try:
        from whatsapp_sender import format_affiliate_message
        print("✓ Módulo whatsapp_sender.py OK")
    except Exception as e:
        print(f"✗ whatsapp_sender.py: {e}")
        return False
    
    try:
        from bot_integrated import scrape_mercadolivre_offers
        print("✓ Módulo bot_integrated.py OK")
    except Exception as e:
        print(f"✗ bot_integrated.py: {e}")
        return False
    
    try:
        from utils.email_handler import EmailHandler
        print("✓ Módulo email_handler.py OK")
    except Exception as e:
        print(f"✗ email_handler.py: {e}")
        return False
    
    print()
    return True


def test_chrome_driver():
    """Testa se o ChromeDriver está acessível"""
    print("🧪 Testando ChromeDriver...")
    
    try:
        from utils.environment import create_driver
        
        print("   Criando driver (isso pode demorar um pouco)...")
        driver = create_driver(headless=True)
        
        print("   Testando navegação...")
        driver.get("https://www.google.com")
        
        if "Google" in driver.title:
            print("✓ ChromeDriver funcionando corretamente")
            print(f"✓ Título da página: {driver.title}")
        else:
            print("⚠️  ChromeDriver abriu, mas página não carregou")
        
        driver.quit()
        print()
        return True
        
    except Exception as e:
        print(f"✗ ChromeDriver: {e}")
        print("   Certifique-se de que o Chrome está instalado")
        print()
        return False


def test_docker_specific():
    """Testes específicos para ambiente Docker"""
    from utils.environment import is_running_in_docker
    
    if not is_running_in_docker():
        return True
    
    print("🧪 Testando configurações Docker...")
    
    # Testa Xvfb
    display = os.environ.get('DISPLAY', '')
    if display:
        print(f"✓ DISPLAY configurado: {display}")
    else:
        print("⚠️  DISPLAY não configurado")
    
    # Testa volumes
    output_dir = '/app/outputs'
    if os.path.exists(output_dir):
        print(f"✓ Volume outputs montado: {output_dir}")
        # Testa escrita
        try:
            test_file = os.path.join(output_dir, '.test_write')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print("✓ Permissão de escrita OK")
        except Exception as e:
            print(f"✗ Erro ao escrever: {e}")
    
    # Testa ChromeDriver Linux
    chromedriver = '/app/utils/chromedriver-linux64/chromedriver'
    if os.path.exists(chromedriver):
        print(f"✓ ChromeDriver Linux encontrado")
        # Verifica permissões
        if os.access(chromedriver, os.X_OK):
            print("✓ Permissões de execução OK")
        else:
            print("⚠️  ChromeDriver sem permissão de execução")
    
    print()
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TESTE DE CONFIGURAÇÃO DO BOT")
    print("=" * 60)
    print()
    
    all_ok = True
    
    test_environment()
    
    if not test_imports():
        all_ok = False
        print("\n⚠️  Instale as dependências: pip install -r requirements.txt\n")
    
    if not test_account_file():
        all_ok = False
    
    if not test_modules():
        all_ok = False
    
    if not test_docker_specific():
        all_ok = False
    
    # ChromeDriver test (opcional, pode demorar)
    print("⏳ Teste do ChromeDriver pode demorar...")
    print("   Pressione Ctrl+C para pular este teste")
    print()
    
    try:
        import time
        time.sleep(2)
        if not test_chrome_driver():
            all_ok = False
    except KeyboardInterrupt:
        print("\n⏭️  Teste do ChromeDriver pulado\n")
    
    print("=" * 60)
    if all_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
    print("=" * 60)
    (Opcional) Configure e-mail para 2FA: EMAIL_2FA_SETUP.md")
        print("   5. Execute novamente: python test_setup.py")
    else:
        print("   🚀 Tudo pronto! Execute o bot:")
        print("      python run_bot.py")
        print()
        print("   🐳 Ou com Docker/Podman:")
        print("      ./run-podman.sh")
        print()
        print("   📚 Consulte a documentação:")
        print("      - MANUAL_USO.md - Guia completo")
        print("      - PODMAN_GUIDE.md - Uso com containers")
        print("      - EMAIL_2FA_SETUP.md - Configurar 2FA automático
        print()
        print("   🐳 Ou com Docker/Podman:")
        print("      ./run-podman.sh")
        print()
        print("   📚 Consulte a documentação:")
        print("      - MANUAL_USO.md - Guia completo")
        print("      - PODMAN_GUIDE.md - Uso com containers")
        print("      - QUICKSTART.md - Início rápido")
    
    sys.exit(0 if all_ok else 1)
