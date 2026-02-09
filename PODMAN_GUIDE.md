# 🐳 Guia de Uso com Podman/Docker

Este guia mostra como executar o bot em containers Linux usando Podman ou Docker.

## 📋 Pré-requisitos

### Instalar Podman (Recomendado) ou Docker

**Linux:**
```bash
# Fedora/RHEL/CentOS
sudo dnf install podman podman-compose

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install podman podman-compose

# Arch Linux
sudo pacman -S podman podman-compose
```

**Windows:**
```powershell
# Podman Desktop (recomendado)
# Download: https://podman-desktop.io/downloads

# Ou Docker Desktop
# Download: https://www.docker.com/products/docker-desktop/
```

**macOS:**
```bash
brew install podman podman-compose
```

## 🚀 Início Rápido

### Método 1: Script Automático (Linux/macOS)

```bash
# Dar permissão de execução
chmod +x run-podman.sh

# Executar script
./run-podman.sh
```

O script apresentará um menu interativo:
```
1) Construir imagem
2) Rodar bot (container único)
3) Rodar com compose
4) Rodar testes
5) Shell interativo
6) Limpar containers/imagens
7) Sair
```

### Método 2: Script Automático (Windows)

```cmd
# No PowerShell ou CMD
run-podman.bat
```

### Método 3: Comandos Manuais

#### 1. Configurar Credenciais

Edite o arquivo [account.txt](account.txt):

```
login = seu_email@mercadolivre.com
password = sua_senha_segura
```

#### 2. Construir Imagem

```bash
# Com Podman
podman build -t bot-mercadolivre:latest .

# Com Docker
docker build -t bot-mercadolivre:latest .
```

#### 3. Executar o Bot

**Comando simples:**

```bash
# Podman
podman run --rm \
  --name bot-mercadolivre \
  -e PYTHONUNBUFFERED=1 \
  -e IN_DOCKER=true \
  -e DISPLAY=:99 \
  -v ./outputs:/app/outputs:z \
  -v ./account.txt:/app/account.txt:ro,z \
  bot-mercadolivre:latest

# Docker
docker run --rm \
  --name bot-mercadolivre \
  -e PYTHONUNBUFFERED=1 \
  -e IN_DOCKER=true \
  -e DISPLAY=:99 \
  -v ./outputs:/app/outputs \
  -v ./account.txt:/app/account.txt:ro \
  bot-mercadolivre:latest
```

**Com Docker Compose:**

```bash
# Podman
podman-compose up --build

# Docker
docker compose up --build
```

## 📂 Estrutura de Volumes

```
./outputs/          → Arquivos Excel gerados
./account.txt       → Credenciais (read-only)
```

Os arquivos Excel gerados pelo bot serão salvos em `./outputs/` no seu host.

## 🔧 Configurações Avançadas

### Variáveis de Ambiente

Você pode personalizar o comportamento através de variáveis de ambiente:

```bash
podman run --rm \
  -e PYTHONUNBUFFERED=1 \
  -e IN_DOCKER=true \
  -e DISPLAY=:99 \
  -e MAX_PAGES=5 \                    # Páginas para coletar
  -e USE_AFFILIATE=true \              # Gerar links de afiliado
  -e SEND_WHATSAPP=false \            # Enviar WhatsApp
  -v ./outputs:/app/outputs:z \
  -v ./account.txt:/app/account.txt:ro,z \
  bot-mercadolivre:latest
```

### Executar Script Customizado

```bash
# Rodar apenas coleta (bot.py original)
podman run --rm \
  -v ./outputs:/app/outputs:z \
  bot-mercadolivre:latest \
  python bot.py

# Rodar testes
podman run --rm \
  -v ./account.txt:/app/account.txt:ro,z \
  bot-mercadolivre:latest \
  python test_setup.py

# Rodar bot integrado
podman run --rm \
  -v ./outputs:/app/outputs:z \
  -v ./account.txt:/app/account.txt:ro,z \
  bot-mercadolivre:latest \
  python bot_integrated.py
```

### Shell Interativo

Para explorar o container:

```bash
# Podman
podman run --rm -it \
  -v ./outputs:/app:z \
  bot-mercadolivre:latest \
  /bin/bash

# Docker
docker run --rm -it \
  -v ./outputs:/app \
  bot-mercadolivre:latest \
  /bin/bash
```

## 📊 Recursos do Container

### Limites Padrão (docker-compose.yml)

```yaml
resources:
  limits:
    cpus: '2.0'
    memory: 2G
  reservations:
    cpus: '1.0'
    memory: 1G
```

### Ajustar Recursos Manualmente

```bash
# Limitar CPU e memória
podman run --rm \
  --cpus=1.5 \
  --memory=1g \
  -v ./outputs:/app/outputs:z \
  bot-mercadolivre:latest
```

## 🐛 Troubleshooting

### Erro: "ChromeDriver não encontrado"

**Solução:** O Dockerfile já inclui e configura o ChromeDriver do Linux. Certifique-se de que a build foi concluída com sucesso.

```bash
# Rebuild forçado
podman build --no-cache -t bot-mercadolivre:latest .
```

### Erro: "Permission denied" no Linux

**Problema:** SELinux bloqueando volumes.

**Solução:** Use a flag `:z` nos volumes:

```bash
-v ./outputs:/app/outputs:z
```

### Container não inicia

**Verificar logs:**

```bash
# Podman
podman logs bot-mercadolivre

# Docker
docker logs bot-mercadolivre
```

**Verificar se a imagem foi construída:**

```bash
# Podman
podman images bot-mercadolivre

# Docker
docker images bot-mercadolivre
```

### Display/Xvfb não funciona

O container já está configurado com Xvfb virtual display. Se ainda houver problemas:

```bash
# Verificar se DISPLAY está setado
podman run --rm bot-mercadolivre:latest env | grep DISPLAY
# Deve mostrar: DISPLAY=:99
```

### Erro de conexão no Mercado Livre

**Possíveis causas:**
- Network do container sem acesso à internet
- Firewall bloqueando
- Rate limiting do site

**Testar conectividade:**

```bash
podman run --rm bot-mercadolivre:latest \
  curl -I https://www.mercadolivre.com.br
```

## 🔒 Segurança

### Práticas Recomendadas

1. **Nunca commite credenciais:**
   - `.gitignore` já está configurado
   - Use secrets do GitHub Actions para CI/CD

2. **Execute com usuário não-root (opcional):**

```bash
# Adicione ao Dockerfile:
RUN useradd -m botuser
USER botuser
```

3. **Volumes read-only quando possível:**

```bash
-v ./account.txt:/app/account.txt:ro,z
```

4. **Remova containers após uso:**

```bash
--rm  # Remove automaticamente quando parar
```

## 📈 Monitoramento

### Ver containers em execução

```bash
# Podman
podman ps

# Docker
docker ps
```

### Ver uso de recursos

```bash
# Podman
podman stats bot-mercadolivre

# Docker
docker stats bot-mercadolivre
```

### Logs em tempo real

```bash
# Podman
podman logs -f bot-mercadolivre

# Docker
docker logs -f bot-mercadolivre
```

## 🧹 Limpeza

### Remover container específico

```bash
# Parar
podman stop bot-mercadolivre

# Remover
podman rm bot-mercadolivre
```

### Remover imagem

```bash
podman rmi bot-mercadolivre:latest
```

### Limpar tudo (cuidado!)

```bash
# Remove todos containers parados
podman container prune

# Remove todas imagens não usadas
podman image prune -a

# Limpar volumes órfãos
podman volume prune
```

## 🚀 Deploy em Servidor

### Executar como serviço (systemd)

1. Criar arquivo de serviço: `/etc/systemd/system/bot-mercadolivre.service`

```ini
[Unit]
Description=Bot Mercado Livre
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/para/Python_Divulg_Whats
ExecStart=/usr/bin/podman run --rm \
  --name bot-mercadolivre \
  -e PYTHONUNBUFFERED=1 \
  -e IN_DOCKER=true \
  -v /caminho/para/outputs:/app/outputs:z \
  -v /caminho/para/account.txt:/app/account.txt:ro,z \
  bot-mercadolivre:latest
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. Habilitar e iniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bot-mercadolivre
sudo systemctl start bot-mercadolivre
sudo systemctl status bot-mercadolivre
```

### Agendar com Cron

```bash
# Editar crontab
crontab -e

# Executar todo dia às 9h
0 9 * * * cd /caminho/para/Python_Divulg_Whats && /usr/bin/podman run --rm -v ./outputs:/app/outputs:z -v ./account.txt:/app/account.txt:ro,z bot-mercadolivre:latest
```

## 📚 Referências

- [Podman Documentation](https://docs.podman.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Podman vs Docker](https://docs.podman.io/en/latest/Introduction.html)
- [ChromeDriver Documentation](https://chromedriver.chromium.org/)

---

⭐ Se encontrou problemas ou tem sugestões, abra uma issue no repositório!
