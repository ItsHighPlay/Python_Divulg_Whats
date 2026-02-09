# Quickstart Guide - Bot Mercado Livre

Este guia rápido te ajuda a começar em minutos!

## 🎯 3 Passos para Começar

### 1️⃣ Configurar Credenciais

Edite o arquivo `account.txt`:

```
login = seu_email@mercadolivre.com
password = sua_senha_segura
```

### 2️⃣ Escolher Método de Execução

<table>
<tr>
<td width="50%">

#### 🐳 **Container (Recomendado para Linux)**

```bash
# Linux/macOS
./run-podman.sh

# Windows
run-podman.bat
```

**Prós:**
- ✅ Isolado
- ✅ ChromeDriver já configurado
- ✅ Funciona em qualquer Linux

</td>
<td width="50%">

#### 💻 **Local (Direto no sistema)**

```bash
# Instalar
pip install -r requirements.txt

# Executar
python run_bot.py
```

**Prós:**
- ✅ Mais rápido
- ✅ Fácil debug
- ✅ Sem Docker necessário

</td>
</tr>
</table>

### 3️⃣ Executar!

```bash
# Com Make (Linux/macOS)
make run

# Com Python
python run_bot.py

# Com Container
./run-podman.sh
```

## 💡 Dicas Rápidas

### Apenas coletar ofertas (sem afiliados)

```bash
python bot.py
```

### Testar configuração

```bash
python test_setup.py
```

### Ver resultados

```bash
# Arquivos Excel em:
./outputs/ofertas_dia_YYYY-MM-DD.xlsx
```

### Customizar quantidade de páginas

Edite `run_bot.py`:

```python
MAX_PAGES = 5  # Coleta 5 páginas
```

## ❓ Problemas Comuns

| Problema | Solução |
|----------|---------|
| ChromeDriver não encontrado | Já está incluído no projeto |
| Credenciais vazias | Edite `account.txt` |
| Selenium não instalado | `pip install -r requirements.txt` |
| WhatsApp não abre | Configure WhatsApp Web primeiro |

## 📚 Documentação Completa

- **[Manual Completo](MANUAL_USO.md)** - Todas as funcionalidades
- **[Guia Podman/Docker](PODMAN_GUIDE.md)** - Uso com containers
- **[README Principal](README.md)** - Visão geral do projeto

---

🚀 **Pronto! Agora é só usar!**
