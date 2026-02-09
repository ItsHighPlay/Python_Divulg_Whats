"""
Bot Principal - Coleta ofertas do Mercado Livre, gera links de afiliado e envia no WhatsApp
"""
import xlsxwriter
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from utils.support import wait_for_element
from selenium.webdriver.chrome.options import Options
from art import text2art
from datetime import date
import os
from affiliate import (
    load_account_credentials,
    login_mercado_livre,
    generate_affiliate_links,
    create_affiliate_driver
)
from whatsapp_sender import send_batch_messages, send_summary_message
from utils.environment import create_driver, get_output_directory


def scrape_mercadolivre_offers(max_pages=3, headless=True):
    """
    Coleta ofertas do Mercado Livre e salva em Excel
    
    :param max_pages: Número máximo de páginas para coletar
    :param headless: Executar em modo headless
    :return: Lista de dicionários com dados dos produtos e nome do arquivo Excel
    """
    print("=" * 60)
    print("🤖 BOT DE COLETA DE OFERTAS - MERCADO LIVRE")
    print("=" * 60)
    
    # Configuração do Excel
    output_dir = get_output_directory()
    filename = os.path.join(output_dir, f'ofertas_dia_{date.today()}.xlsx')
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet('Ofertas do MercadoLivre')
    
    # Contadores de linhas
    row = row1 = row2 = row3 = row4 = 1
    
    # Cabeçalhos
    worksheet.write(0, 0, 'Produtos')
    worksheet.write(0, 1, 'Preço')
    worksheet.write(0, 2, 'Preço anterior')
    worksheet.write(0, 3, 'Desconto')
    worksheet.write(0, 4, 'Link')
    
    # Configuração do Selenium - usa detecção automática de ambiente
    driver: WebDriver = create_driver(headless=headless)
    
    try:
        driver.get("https://www.mercadolivre.com.br/ofertas")
        print("\n✓ Página de ofertas carregada")
        
        # Determina o número total de páginas
        try:
            pages_element = driver.find_element(By.XPATH, '/html/body/main/div/div[2]/div[2]/div/ul/li[12]/a')
            total_pages = int(pages_element.get_attribute('innerHTML'))
            pages_to_scrape = min(total_pages, max_pages)
        except:
            print("⚠️  Não foi possível determinar o número de páginas. Usando máximo de 3.")
            pages_to_scrape = 3
        
        print(f"\n📄 Total de páginas a coletar: {pages_to_scrape}")
        
        products_data = []
        
        for page in range(pages_to_scrape):
            print(f"\n🔍 Coletando página {page + 1} de {pages_to_scrape}...")
            
            # Coleta nomes
            for names in driver.find_elements(By.CLASS_NAME, 'promotion-item__title'):
                worksheet.write(row, 0, names.get_attribute('innerHTML'))
                row += 1
            
            # Coleta preços
            for price in driver.find_elements(By.CLASS_NAME, 'promotion-item__price'):
                try:
                    real = price.find_element(By.TAG_NAME, 'span')
                    try:
                        cents = price.find_element(By.TAG_NAME, 'sup')
                        price_text = real.text + ',' + cents.text
                    except NoSuchElementException:
                        price_text = real.text
                    worksheet.write(row1, 1, price_text)
                    row1 += 1
                except:
                    row1 += 1
            
            # Coleta preços antigos
            for old_price in driver.find_elements(By.CLASS_NAME, 'promotion-item__oldprice'):
                worksheet.write(row2, 2, old_price.text)
                row2 += 1
            
            # Coleta descontos
            for discount in driver.find_elements(By.CLASS_NAME, 'promotion-item__discount'):
                discount_text = discount.text.strip()
                if discount_text:
                    # Extrai apenas a porcentagem
                    discount_value = discount_text.split('%')[0] + '% OFF'
                else:
                    discount_value = 'N/A'
                worksheet.write(row3, 3, discount_value)
                row3 += 1
            
            # Coleta links
            links_collected = []
            for link in driver.find_elements(By.CLASS_NAME, 'promotion-item__link-container'):
                href = link.get_attribute('href')
                worksheet.write_url(row4, 4, href, string='Link')
                links_collected.append(href)
                row4 += 1
            
            print(f"✓ Coletados {len(links_collected)} produtos da página {page + 1}")
            
            # Navega para próxima página
            if page + 1 < pages_to_scrape:
                driver.get(f'https://www.mercadolivre.com.br/ofertas?page={page + 2}')
                wait_for_element(driver, (By.CLASS_NAME, 'promotion-item__title'))
        
        # Fecha o workbook para salvar
        workbook.close()
        print(f"\n✓ Dados salvos em: {filename}")
        
        # Lê os dados do Excel para retornar
        print("\n📊 Processando dados coletados...")
        for i in range(1, row):
            try:
                product = {
                    'name': worksheet.table.get((i, 0), 'N/A'),
                    'price': worksheet.table.get((i, 1), 'N/A'),
                    'old_price': worksheet.table.get((i, 2), 'N/A'),
                    'discount': worksheet.table.get((i, 3), 'N/A'),
                    'link': worksheet.table.get((i, 4), '')
                }
                products_data.append(product)
            except:
                continue
        
        print(f"✓ Total de produtos processados: {len(products_data)}")
        
    finally:
        driver.quit()
    
    return products_data, filename


def main_with_affiliate_integration(
    whatsapp_number: str = None,
    max_pages: int = 2,
    use_affiliate: bool = True,
    send_whatsapp: bool = False
):
    """
    Função principal que integra todas as funcionalidades
    
    :param whatsapp_number: Número do WhatsApp para enviar (formato: +5511999999999)
    :param max_pages: Número máximo de páginas para coletar
    :param use_affiliate: Se deve gerar links de afiliado
    :param send_whatsapp: Se deve enviar mensagens no WhatsApp
    """
    try:
        byebye = text2art("KvnBarrios")
        
        # Passo 1: Coleta ofertas do Mercado Livre
        print("\n" + "=" * 60)
        print("PASSO 1: Coletando ofertas do Mercado Livre")
        print("=" * 60)
        products_data, excel_file = scrape_mercadolivre_offers(max_pages=max_pages, headless=True)
        
        if not products_data:
            print("❌ Nenhum produto coletado. Encerrando...")
            return
        
        # Passo 2: Gera links de afiliado (se ativado)
        affiliate_links = []
        if use_affiliate:
            print("\n" + "=" * 60)
            print("PASSO 2: Gerando links de afiliado")
            print("=" * 60)
            
            try:
                # Carrega credenciais
                email, password = load_account_credentials()
                print(f"✓ Credenciais carregadas: {email[:3]}***@***")
                
                # Cria driver para afiliados
                affiliate_driver = create_affiliate_driver(headless=False)
                
                # Faz login
                if login_mercado_livre(affiliate_driver, email, password):
                    # Extrai URLs dos produtos
                    product_urls = [p['link'] for p in products_data if p.get('link')]
                    
                    # Gera links de afiliado
                    affiliate_links = generate_affiliate_links(
                        affiliate_driver,
                        product_urls[:20]  # Limita a 20 produtos para teste
                    )
                    
                    # Atualiza os produtos com links de afiliado
                    for i, link in enumerate(affiliate_links):
                        if i < len(products_data):
                            products_data[i]['link'] = link
                    
                    print(f"✓ {len(affiliate_links)} links de afiliado gerados")
                else:
                    print("❌ Falha no login. Usando links originais.")
                
                affiliate_driver.quit()
                
            except Exception as e:
                print(f"❌ Erro ao gerar links de afiliado: {str(e)}")
                print("Continuando com links originais...")
        
        # Passo 3: Envia mensagens no WhatsApp (se ativado)
        if send_whatsapp and whatsapp_number:
            print("\n" + "=" * 60)
            print("PASSO 3: Enviando mensagens no WhatsApp")
            print("=" * 60)
            
            try:
                # Prepara dados para envio
                products_to_send = []
                for product in products_data[:10]:  # Envia apenas primeiros 10
                    products_to_send.append({
                        'name': product.get('name', 'Produto sem nome'),
                        'price': product.get('price', 'N/A'),
                        'discount': product.get('discount', 'N/A'),
                        'link': product.get('link', '')
                    })
                
                # Envia mensagem resumo
                send_summary_message(whatsapp_number, products_to_send, wait_time=15)
                
                print("\n✓ Mensagens agendadas no WhatsApp!")
                print("⚠️  Não feche o navegador durante o envio")
                
            except Exception as e:
                print(f"❌ Erro ao enviar mensagens: {str(e)}")
        
        # Finalização
        print("\n" + "=" * 60)
        print("✅ BOT FINALIZADO COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo salvo: {excel_file}")
        print(f"📊 Total de produtos: {len(products_data)}")
        if affiliate_links:
            print(f"🔗 Links de afiliado: {len(affiliate_links)}")
        print("\n" + byebye)
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Configuração de exemplo
    print("=" * 60)
    print("🤖 BOT DE OFERTAS MERCADO LIVRE + AFILIADOS + WHATSAPP")
    print("=" * 60)
    print("\n⚙️  CONFIGURAÇÃO:")
    print("- Coletar ofertas: SIM")
    print("- Gerar links de afiliado: SIM")
    print("- Enviar WhatsApp: NÃO (altere send_whatsapp=True para ativar)")
    print("\n" + "=" * 60)
    
    # Execute o bot
    main_with_affiliate_integration(
        whatsapp_number="+5511999999999",  # ⚠️  ALTERE PARA SEU NÚMERO
        max_pages=2,                        # Número de páginas para coletar
        use_affiliate=True,                 # Ativa geração de links de afiliado
        send_whatsapp=False                 # ⚠️  Mude para True para enviar WhatsApp
    )
