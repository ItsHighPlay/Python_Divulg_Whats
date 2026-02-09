"""
Módulo para enviar mensagens do WhatsApp com links de afiliado
"""
import pywhatkit as kit
import time
from datetime import datetime, timedelta


def format_affiliate_message(product_name: str, price: str, discount: str, affiliate_link: str):
    """
    Formata uma mensagem de promoção para WhatsApp
    
    :param product_name: Nome do produto
    :param price: Preço do produto
    :param discount: Desconto aplicado
    :param affiliate_link: Link de afiliado
    :return: Mensagem formatada
    """
    message = f"""
🔥 *OFERTA IMPERDÍVEL!* 🔥

📦 {product_name}

💰 *Preço:* R$ {price}
🎯 *Desconto:* {discount}

🛒 Compre agora: {affiliate_link}

⚡ Aproveite antes que acabe!
"""
    return message.strip()


def send_whatsapp_message(phone_number: str, message: str, wait_time: int = 15):
    """
    Envia uma mensagem instantânea no WhatsApp
    
    :param phone_number: Número de telefone com código do país (+55...)
    :param message: Mensagem a ser enviada
    :param wait_time: Tempo de espera em segundos antes de enviar (padrão: 15)
    :return: True se enviado com sucesso
    """
    try:
        print(f"Preparando para enviar mensagem para {phone_number}...")
        
        # Calcula a hora atual + wait_time segundos
        now = datetime.now()
        send_time = now + timedelta(seconds=wait_time)
        
        hour = send_time.hour
        minute = send_time.minute
        
        print(f"Mensagem agendada para {hour:02d}:{minute:02d}")
        
        # Envia a mensagem
        kit.sendwhatmsg(phone_number, message, hour, minute, wait_time=15, tab_close=True)
        
        print("✓ Mensagem enviada com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar mensagem: {str(e)}")
        return False


def send_batch_messages(phone_number: str, products: list, interval: int = 120):
    """
    Envia múltiplas mensagens em lote com intervalo entre elas
    
    :param phone_number: Número de telefone ou grupo
    :param products: Lista de dicionários com dados dos produtos
                     [{'name': str, 'price': str, 'discount': str, 'link': str}]
    :param interval: Intervalo em segundos entre mensagens (padrão: 120s/2min)
    :return: Número de mensagens enviadas com sucesso
    """
    success_count = 0
    total = len(products)
    
    print(f"\n=== Iniciando envio de {total} mensagens ===")
    print(f"Intervalo entre mensagens: {interval} segundos\n")
    
    for idx, product in enumerate(products, 1):
        try:
            print(f"[{idx}/{total}] Enviando: {product['name'][:50]}...")
            
            # Formata a mensagem
            message = format_affiliate_message(
                product['name'],
                product['price'],
                product['discount'],
                product['link']
            )
            
            # Calcula o tempo de espera para esta mensagem
            wait_time = 15 + (interval * idx)
            
            # Envia a mensagem
            if send_whatsapp_message(phone_number, message, wait_time):
                success_count += 1
                print(f"✓ Mensagem {idx}/{total} agendada\n")
            else:
                print(f"✗ Falha ao enviar mensagem {idx}/{total}\n")
            
            # Aguarda um pouco entre os agendamentos
            if idx < total:
                time.sleep(2)
                
        except Exception as e:
            print(f"Erro ao processar produto {idx}: {str(e)}\n")
            continue
    
    print(f"\n=== Envio concluído: {success_count}/{total} mensagens agendadas ===")
    return success_count


def send_summary_message(phone_number: str, products: list, wait_time: int = 15):
    """
    Envia uma mensagem resumo com várias ofertas
    
    :param phone_number: Número de telefone ou grupo
    :param products: Lista de produtos
    :param wait_time: Tempo de espera antes de enviar
    :return: True se enviado com sucesso
    """
    try:
        message = "🔥 *OFERTAS DO DIA - MERCADO LIVRE* 🔥\n\n"
        
        for idx, product in enumerate(products[:10], 1):  # Limita a 10 produtos
            message += f"{idx}. *{product['name'][:40]}...*\n"
            message += f"   💰 R$ {product['price']} | {product['discount']}\n"
            message += f"   🔗 {product['link']}\n\n"
        
        message += "⚡ *Aproveite essas ofertas imperdíveis!*"
        
        return send_whatsapp_message(phone_number, message, wait_time)
        
    except Exception as e:
        print(f"Erro ao enviar mensagem resumo: {str(e)}")
        return False


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Módulo WhatsApp ===\n")
    
    # Dados de teste
    test_phone = "+5511999999999"  # Substitua pelo seu número
    test_products = [
        {
            'name': 'Apple iPhone 13 128GB - Meia-noite',
            'price': '3.499,00',
            'discount': '15% OFF',
            'link': 'https://mercadolivre.com/sec/example1'
        },
        {
            'name': 'Notebook Dell Inspiron 15',
            'price': '2.899,00',
            'discount': '20% OFF',
            'link': 'https://mercadolivre.com/sec/example2'
        }
    ]
    
    print("Teste de formatação de mensagem:")
    print("-" * 50)
    test_message = format_affiliate_message(
        test_products[0]['name'],
        test_products[0]['price'],
        test_products[0]['discount'],
        test_products[0]['link']
    )
    print(test_message)
    print("-" * 50)
    
    print("\n⚠️  Para testar o envio real, descomente o código abaixo e adicione um número válido")
    # send_summary_message(test_phone, test_products)
