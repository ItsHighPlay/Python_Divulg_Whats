# 🔐 Verificação 2FA Automática - Resumo da Implementação

## ✅ O que foi implementado:

### 1. **Módulo de E-mail** (`utils/email_handler.py`)

Funcionalidades principais:
- ✅ Conexão IMAP com Gmail, Outlook, Yahoo
- ✅ Busca automática de e-mails do Mercado Livre
- ✅ Extração de códigos de verificação usando regex
- ✅ Suporte a múltiplos formatos de código
- ✅ Retry automático com timeout configurável
- ✅ Decode de assuntos e corpos de e-mail
- ✅ Tratamento de e-mails HTML e texto plano

**Padrões de código suportados:**
- `123456` (6 dígitos)
- `código: 123456`
- `code: 123456`
- `token: 123456`
- Códigos de 4 a 8 dígitos

### 2. **Login com 2FA** (modificado `affiliate.py`)

Melhorias no processo de login:
- ✅ Detecção automática de solicitação de código
- ✅ Múltiplos indicadores de verificação (ID, name, placeholder, xpath)
- ✅ Solicita código por e-mail (se disponível)
- ✅ Busca código no e-mail automaticamente
- ✅ Insere código no campo correto
- ✅ Submete formulário de verificação
- ✅ Fallback para entrada manual (60s de espera)
- ✅ Tratamento de erros robusto

### 3. **Configuração Simplificada**

Arquivos atualizados:
- ✅ `account.txt.example` - Template com campos de e-mail
- ✅ `requirements.txt` - Adicionado `imap-tools`
- ✅ `EMAIL_2FA_SETUP.md` - Guia completo de configuração
- ✅ `README.md` - Documentação atualizada
- ✅ `test_setup.py` - Testes de e-mail incluídos

## 🚀 Como usar:

### **Configuração Básica** (5 minutos)

1. **Habilitar IMAP no Gmail:**
   - Configurações → Encaminhamento e POP/IMAP → Ativar IMAP

2. **Criar Senha de App:**
   - https://myaccount.google.com/apppasswords
   - Gerar senha de 16 caracteres

3. **Configurar account.txt:**
```
login = seu_email_mercadolivre@gmail.com
password = sua_senha_mercadolivre

email = seu_email@gmail.com
email_password = abcd efgh ijkl mnop
```

4. **Testar:**
```bash
python utils/email_handler.py
```

### **Uso Automático**

O bot agora automaticamente:
1. Detecta solicitação de código
2. Busca no e-mail
3. Insere o código
4. Completa o login

```python
from affiliate import create_affiliate_driver, login_mercado_livre

driver = create_affiliate_driver(headless=False)
login_mercado_livre(driver, "email", "senha", handle_2fa=True)
```

## 📊 Fluxo de Verificação 2FA:

```
┌────────────────────┐
│  Login ML          │
│  (email + senha)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  ML solicita       │◄─── Detecção automática
│  código 2FA        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Bot clica em      │
│  "Enviar por       │
│  e-mail"           │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  ML envia código   │
│  por e-mail        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Bot conecta       │
│  ao Gmail (IMAP)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Bot busca e-mail  │
│  (últimos 5 min)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Bot extrai código │
│  com regex         │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Bot insere código │
│  no campo          │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Login completo ✓  │
└────────────────────┘
```

## 🧪 Testes Disponíveis:

### 1. Teste de Conexão:
```bash
python utils/email_handler.py
```

### 2. Teste de Login com 2FA:
```bash
python affiliate.py
```

### 3. Teste Completo do Sistema:
```bash
python test_setup.py
```

## 🔧 Configurações Avançadas:

### Ajustar Tempo de Espera:

```python
# Em affiliate.py, na função _handle_email_verification
verification_code = email_handler.get_verification_code_from_mercadolivre(
    max_attempts=20,  # 20 tentativas (padrão: 12)
    wait_seconds=10   # 10 segundos entre tentativas (padrão: 5)
)
```

### Desabilitar 2FA Automático:

```python
# Usar verificação manual
login_mercado_livre(driver, email, senha, handle_2fa=False)
```

### Outros Provedores de E-mail:

```python
# Outlook
handler = EmailHandler(email, password, provider='outlook')

# Yahoo
handler = EmailHandler(email, password, provider='yahoo')
```

## 🐛 Troubleshooting:

### Código não encontrado?
- ✅ Verifique se IMAP está habilitado
- ✅ Use senha de app (não senha normal)
- ✅ Aguarde mais tempo (aumente `max_attempts`)
- ✅ Verifique se e-mail chegou manualmente

### Erro de autenticação?
- ✅ Gmail: Use senha de app de 16 caracteres
- ✅ Outlook: Use senha normal + "apps menos seguros"
- ✅ Verifique se copiou a senha corretamente

### Campo de código não encontrado?
- ✅ Execute com `headless=False` para debug
- ✅ Página pode ter mudado (atualize locators)
- ✅ Insira manualmente (bot espera 60s)

## 📈 Melhorias Futuras:

Possíveis aprimoramentos:
- [ ] Suporte a Gmail API (mais seguro que IMAP)
- [ ] Cache de códigos usados recentemente
- [ ] Notificação quando código for encontrado
- [ ] Suporte a SMS (via Twilio)
- [ ] Dashboard de monitoramento
- [ ] Logs detalhados em arquivo

## 🔒 Segurança:

**Implementado:**
- ✅ Senhas de app (não senha principal)
- ✅ Conexão SSL/TLS obrigatória
- ✅ Credenciais em .gitignore
- ✅ Sem hardcode de senhas
- ✅ Timeout de segurança

**Recomendações:**
- 🔐 Use senha de app sempre que possível
- 🔐 Revogue senhas não utilizadas
- 🔐 Monitore acessos à conta
- 🔐 Não compartilhe account.txt
- 🔐 Use .env para produção

## 📚 Documentação:

- **[EMAIL_2FA_SETUP.md](EMAIL_2FA_SETUP.md)** - Guia completo de configuração
- **[README.md](README.md)** - Visão geral atualizada
- **[utils/email_handler.py](utils/email_handler.py)** - Código-fonte documentado
- **[affiliate.py](affiliate.py)** - Implementação de login com 2FA

## 💡 Dicas:

1. **Primeira vez:** Execute com `headless=False` para ver o processo
2. **Debug:** Use `print()` nos módulos para acompanhar execução
3. **Performance:** Reduza `wait_seconds` se seu e-mail chega rápido
4. **Backup:** Sempre tenha opção de entrada manual disponível

---

## ✅ Checklist de Implementação:

- [x] Módulo de e-mail (IMAP)
- [x] Detecção de 2FA
- [x] Busca automática de código
- [x] Inserção automática
- [x] Fallback para manual
- [x] Múltiplos provedores
- [x] Tratamento de erros
- [x] Documentação completa
- [x] Testes automatizados
- [x] Exemplos de uso

**Status:** ✅ **Implementação Completa e Funcional**

---

💡 **Para começar:** Siga o guia [EMAIL_2FA_SETUP.md](EMAIL_2FA_SETUP.md) - configuração em 5 minutos! 🚀
