"""
Exemplo básico de envio de mensagens no WhatsApp com pywhatkit
"""
import pywhatkit as kit
from datetime import datetime, timedelta


# Configurações
whatsapp_number = "+5511999999999"  # ⚠️  ALTERE para o número do grupo/contato
message = """
🔥 Olá! Confira nossas ofertas incríveis!

Visite nossa loja e aproveite os descontos especiais!

🛒 Link: https://exemplo.com
"""

# Variáveis de controle
atual_messg = 0
limit_messg = 100  # Limite de mensagens por execução


def send_immediate_message(phone: str, msg: str):
    """
    Envia mensagem imediatamente (em 2 minutos)
    
    :param phone: Número do WhatsApp (+5511999999999)
    :param msg: Mensagem a enviar
    """
    now = datetime.now()
    send_time = now + timedelta(minutes=2)
    
    print(f"Agendando mensagem para {send_time.strftime('%H:%M')}")
    
    kit.sendwhatmsg(
        phone,
        msg,
        send_time.hour,
        send_time.minute,
        wait_time=15,
        tab_close=True
    )
    print("✓ Mensagem enviada!")


def send_scheduled_message(phone: str, msg: str, hour: int, minute: int):
    """
    Envia mensagem em horário específico
    
    :param phone: Número do WhatsApp
    :param msg: Mensagem a enviar
    :param hour: Hora (0-23)
    :param minute: Minuto (0-59)
    """
    print(f"Agendando mensagem para {hour:02d}:{minute:02d}")
    
    kit.sendwhatmsg(
        phone,
        msg,
        hour,
        minute,
        wait_time=15,
        tab_close=True
    )
    print("✓ Mensagem enviada!")


def send_batch_messages(phone: str, messages: list, max_messages: int = 10):
    """
    Envia múltiplas mensagens com intervalo
    
    :param phone: Número do WhatsApp
    :param messages: Lista de mensagens
    :param max_messages: Limite de mensagens
    """
    global atual_messg
    
    messages_to_send = min(len(messages), max_messages)
    
    print(f"Enviando {messages_to_send} mensagens...")
    
    now = datetime.now()
    
    for i, msg in enumerate(messages[:messages_to_send]):
        if atual_messg >= limit_messg:
            print("⚠️  Limite de mensagens atingido!")
            break
        
        # Agenda com 2 minutos de intervalo entre cada mensagem
        send_time = now + timedelta(minutes=2 + (i * 2))
        
        try:
            kit.sendwhatmsg(
                phone,
                msg,
                send_time.hour,
                send_time.minute,
                wait_time=10,
                tab_close=True
            )
            
            atual_messg += 1
            print(f"✓ Mensagem {i+1}/{messages_to_send} agendada para {send_time.strftime('%H:%M')}")
            
        except Exception as e:
            print(f"✗ Erro ao enviar mensagem {i+1}: {str(e)}")
    
    print(f"\n✓ Total enviado: {atual_messg} mensagens")


# Exemplos de uso
if __name__ == "__main__":
    print("=" * 60)
    print("📱 EXEMPLO DE USO - PYWHATKIT")
    print("=" * 60)
    
    print("\n⚠️  ATENÇÃO: Descomente o código abaixo para testar")
    print("⚠️  Altere o número do WhatsApp para um válido\n")
    
    # Exemplo 1: Enviar mensagem imediata
    # send_immediate_message(whatsapp_number, message)
    
    # Exemplo 2: Enviar mensagem agendada (hoje às 15:30)
    # send_scheduled_message(whatsapp_number, message, hour=15, minute=30)
    
    # Exemplo 3: Enviar múltiplas mensagens
    # messages_list = [
    #     "🔥 Oferta 1: Produto X com 20% OFF!",
    #     "🔥 Oferta 2: Produto Y com 30% OFF!",
    #     "🔥 Oferta 3: Produto Z com 15% OFF!"
    # ]
    # send_batch_messages(whatsapp_number, messages_list, max_messages=3)
    
    print("✓ Script finalizado. Descomente o código para testar.")

