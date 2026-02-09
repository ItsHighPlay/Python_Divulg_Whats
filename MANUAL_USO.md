# 🤖 Bot de Ofertas Mercado Livre + Afiliados + WhatsApp

Bot automatizado que coleta ofertas do Mercado Livre, gera links de afiliado e envia mensagens promocionais no WhatsApp.

## 📋 Funcionalidades

✅ **Coleta de Ofertas**: Scraping automático de ofertas do Mercado Livre  
✅ **Geração de Links de Afiliado**: Converte links de produtos em links de afiliado  
✅ **Envio WhatsApp**: Envia mensagens promocionais automaticamente  
✅ **Exportação Excel**: Salva dados em planilha formatada

## 🚀 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciais

Edite o arquivo [account.txt](account.txt) com suas credenciais do Mercado Livre:

```
login = seu_email@exemplo.com
password = sua_senha_segura
```

⚠️ **IMPORTANTE**: Nunca compartilhe este arquivo publicamente!

## 📖 Como Usar

### Opção 1: Bot Completo (Recomendado)

Execute o bot integrado com todas as funcionalidades:

```bash
python bot_integrated.py
```

**O que ele faz:**
1. Coleta ofertas do Mercado Livre (2 páginas por padrão)
2. Faz login na conta de afiliado
3. Gera links de afiliado para os produtos
4. (Opcional) Envia mensagens no WhatsApp

**Configuração no código:**

```python
main_with_affiliate_integration(
    whatsapp_number="+5511999999999",  # Seu número ou grupo
    max_pages=2,                        # Páginas para coletar
    use_affiliate=True,                 # Gerar links de afiliado
    send_whatsapp=False                 # Ativar envio WhatsApp
)
```

### Opção 2: Apenas Coleta de Ofertas

Execute o bot original sem afiliados:

```bash
python bot.py
```

### Opção 3: Módulos Individuais

#### Gerar Links de Afiliado

```python
from affiliate import (
    load_account_credentials,
    login_mercado_livre,
    generate_affiliate_links,
    create_affiliate_driver
)

# Carrega credenciais
email, password = load_account_credentials()

# Cria driver
driver = create_affiliate_driver(headless=False)

# Faz login
login_mercado_livre(driver, email, password)

# Gera links
urls = ["https://www.mercadolivre.com.br/produto-exemplo"]
affiliate_links = generate_affiliate_links(driver, urls)

print(affiliate_links)
driver.quit()
```

#### Enviar Mensagens WhatsApp

```python
from whatsapp_sender import send_whatsapp_message, format_affiliate_message

# Formata mensagem
message = format_affiliate_message(
    product_name="iPhone 13 128GB",
    price="3.499,00",
    discount="15% OFF",
    affiliate_link="https://mercadolivre.com/sec/abc123"
)

# Envia mensagem
send_whatsapp_message("+5511999999999", message, wait_time=15)
```

## 📁 Estrutura do Projeto

```
Python_Divulg_Whats/
├── bot.py                  # Bot original de coleta
├── bot_integrated.py       # Bot completo com todas funcionalidades
├── affiliate.py            # Módulo de links de afiliado
├── whatsapp_sender.py      # Módulo de envio WhatsApp
├── base.py                 # Exemplos básicos de uso
├── account.txt             # Credenciais (não versione!)
├── requirements.txt        # Dependências
└── utils/
    └── support.py          # Funções auxiliares
```

## ⚙️ Configurações Avançadas

### Ajustar Número de Páginas

Altere `max_pages` para coletar mais ou menos ofertas:

```python
main_with_affiliate_integration(max_pages=5)  # Coleta 5 páginas
```

### Executar em Modo Visível (Debugging)

Por padrão, o bot executa com navegador invisível (headless). Para ver o navegador em ação:

```python
# Em affiliate.py
driver = create_affiliate_driver(headless=False)

# Em bot_integrated.py
scrape_mercadolivre_offers(headless=False)
```

### Envio em Lote no WhatsApp

Para enviar várias mensagens com intervalo:

```python
from whatsapp_sender import send_batch_messages

products = [
    {'name': 'Produto 1', 'price': '100,00', 'discount': '10%', 'link': 'http://...'},
    {'name': 'Produto 2', 'price': '200,00', 'discount': '20%', 'link': 'http://...'}
]

send_batch_messages(
    phone_number="+5511999999999",
    products=products,
    interval=120  # 120 segundos entre mensagens
)
```

## 🔧 Resolução de Problemas

### Erro: "ChromeDriver não encontrado"

**Solução**: O ChromeDriver já está incluído na pasta `utils/`. Certifique-se de que:
- Você está no diretório correto
- O Chrome está instalado
- Sua versão do Chrome é compatível

### Erro: "Credenciais vazias"

**Solução**: Edite [account.txt](account.txt) corretamente:
```
login = seu_email@exemplo.com
password = sua_senha
```

### WhatsApp não abre

**Solução**: 
- Certifique-se de que o WhatsApp Web está configurado no seu navegador padrão
- O pywhatkit abre uma aba do navegador automaticamente
- Não feche a janela até a mensagem ser enviada

### Login de Afiliado Falha

**Possíveis causas**:
- Credenciais incorretas
- Verificação de segurança do Mercado Livre
- Conexão instável

**Solução**: Execute com `headless=False` para ver o que está acontecendo.

## ⚠️ Avisos Importantes

1. **Rate Limiting**: Evite executar o bot com muita frequência para não ser bloqueado
2. **WhatsApp**: Respeite as políticas do WhatsApp para evitar banimento
3. **Credenciais**: NUNCA commite o arquivo `account.txt` com dados reais
4. **Uso Ético**: Use responsavelmente e respeite os termos de serviço

## 📊 Exemplo de Saída

```
============================================================
🤖 BOT DE OFERTAS MERCADO LIVRE + AFILIADOS + WHATSAPP
============================================================

⚙️  CONFIGURAÇÃO:
- Coletar ofertas: SIM
- Gerar links de afiliado: SIM
- Enviar WhatsApp: NÃO

============================================================
PASSO 1: Coletando ofertas do Mercado Livre
============================================================

✓ Página de ofertas carregada
📄 Total de páginas a coletar: 2

🔍 Coletando página 1 de 2...
✓ Coletados 20 produtos da página 1

🔍 Coletando página 2 de 2...
✓ Coletados 20 produtos da página 2

✓ Dados salvos em: ofertas_dia_2026-02-09.xlsx
📊 Total de produtos processados: 40

============================================================
PASSO 2: Gerando links de afiliado
============================================================

✓ Credenciais carregadas: joh***@***
Acessando página de login...
Preenchendo email...
Preenchendo senha...
Login realizado com sucesso!

Gerando links de afiliado para 20 produtos...
Processando lote 1 (10 URLs)...
✓ 10 links de afiliado gerados neste lote
Processando lote 2 (10 URLs)...
✓ 10 links de afiliado gerados neste lote

✓ Total de 20 links de afiliado gerados com sucesso!

============================================================
✅ BOT FINALIZADO COM SUCESSO!
============================================================
📁 Arquivo salvo: ofertas_dia_2026-02-09.xlsx
📊 Total de produtos: 40
🔗 Links de afiliado: 20
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se livre para abrir issues ou pull requests.

## 📝 Licença

Este projeto é fornecido "como está" para fins educacionais.

## 👤 Autor

**KvnBarrios**

---

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!
