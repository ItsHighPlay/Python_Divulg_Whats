"""
EXEMPLO SIMPLES DE USO - Bot de Ofertas + Afiliados + WhatsApp
"""

from bot_integrated import main_with_affiliate_integration

# ========================================
# CONFIGURAÇÃO: Edite os valores abaixo
# ========================================

# 1. Número do WhatsApp (formato: +55DDDNÚMERO)
#    Exemplo: +5511987654321
WHATSAPP_NUMBER = "+5511999999999"  # ⚠️ ALTERE AQUI

# 2. Número de páginas do Mercado Livre para coletar
#    Cada página tem aproximadamente 20 produtos
MAX_PAGES = 2

# 3. Gerar links de afiliado?
#    True = Sim | False = Não
#    Requer credenciais válidas no account.txt
USE_AFFILIATE = True

# 4. Enviar mensagens no WhatsApp?
#    True = Sim | False = Não
#    ⚠️ ATENÇÃO: Ao ativar, mensagens serão enviadas automaticamente!
SEND_WHATSAPP = False  # ⚠️ Mude para True quando estiver pronto

# ========================================
# EXECUÇÃO DO BOT
# ========================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" 🤖 BOT DE OFERTAS - MERCADO LIVRE")
    print("=" * 70)
    print("\n📋 CONFIGURAÇÃO ATUAL:")
    print(f"   • Número WhatsApp: {WHATSAPP_NUMBER}")
    print(f"   • Páginas para coletar: {MAX_PAGES}")
    print(f"   • Gerar links de afiliado: {'✓ SIM' if USE_AFFILIATE else '✗ NÃO'}")
    print(f"   • Enviar WhatsApp: {'✓ SIM' if SEND_WHATSAPP else '✗ NÃO'}")
    
    if not SEND_WHATSAPP:
        print("\n⚠️  ENVIO DE WHATSAPP DESATIVADO")
        print("   Altere SEND_WHATSAPP = True para ativar")
    
    print("\n" + "=" * 70)
    
    # Confirmação de segurança
    if SEND_WHATSAPP:
        resposta = input("\n⚠️  Mensagens serão enviadas! Deseja continuar? (S/N): ")
        if resposta.upper() != 'S':
            print("❌ Operação cancelada.")
            exit()
    
    # Executa o bot
    print("\n🚀 Iniciando bot...\n")
    
    try:
        main_with_affiliate_integration(
            whatsapp_number=WHATSAPP_NUMBER,
            max_pages=MAX_PAGES,
            use_affiliate=USE_AFFILIATE,
            send_whatsapp=SEND_WHATSAPP
        )
    except KeyboardInterrupt:
        print("\n\n❌ Bot interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        import traceback
        traceback.print_exc()
