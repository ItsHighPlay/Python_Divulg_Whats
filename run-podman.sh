#!/bin/bash

# Script para rodar o bot com Podman
# Compatível com Docker também

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🤖 Bot Mercado Livre - Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detecta se está usando Podman ou Docker
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    echo -e "${GREEN}✓ Podman detectado${NC}"
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker compose"
    echo -e "${GREEN}✓ Docker detectado${NC}"
else
    echo -e "${RED}✗ Erro: Nem Podman nem Docker foram encontrados${NC}"
    echo -e "${YELLOW}Instale um dos dois:${NC}"
    echo "  - Podman: https://podman.io/getting-started/installation"
    echo "  - Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verifica se o arquivo de credenciais existe
if [ ! -f "account.txt" ]; then
    echo -e "${YELLOW}⚠️  Arquivo account.txt não encontrado${NC}"
    echo "Criando arquivo de exemplo..."
    cat > account.txt << EOF
login = seu_email@exemplo.com
password = sua_senha_segura
EOF
    echo -e "${GREEN}✓ Arquivo account.txt criado${NC}"
    echo -e "${RED}⚠️  IMPORTANTE: Edite o arquivo account.txt com suas credenciais antes de continuar${NC}"
    exit 1
fi

# Cria diretório de outputs se não existir
mkdir -p outputs

# Função para construir a imagem
build_image() {
    echo ""
    echo -e "${BLUE}🔨 Construindo imagem...${NC}"
    $CONTAINER_CMD build -t bot-mercadolivre:latest .
    echo -e "${GREEN}✓ Imagem construída com sucesso${NC}"
}

# Função para rodar o bot
run_bot() {
    echo ""
    echo -e "${BLUE}🚀 Iniciando bot...${NC}"
    
    $CONTAINER_CMD run --rm \
        --name bot-mercadolivre \
        -e PYTHONUNBUFFERED=1 \
        -e IN_DOCKER=true \
        -e DISPLAY=:99 \
        -v "$(pwd)/outputs:/app/outputs:z" \
        -v "$(pwd)/account.txt:/app/account.txt:ro,z" \
        bot-mercadolivre:latest
    
    echo ""
    echo -e "${GREEN}✓ Bot finalizado${NC}"
    echo -e "${BLUE}📁 Arquivos salvos em: ./outputs/${NC}"
}

# Função para rodar com docker-compose/podman-compose
run_compose() {
    echo ""
    echo -e "${BLUE}🚀 Iniciando com $COMPOSE_CMD...${NC}"
    
    if [ "$CONTAINER_CMD" = "podman" ]; then
        if ! command -v podman-compose &> /dev/null; then
            echo -e "${YELLOW}⚠️  podman-compose não encontrado. Instalando...${NC}"
            pip3 install podman-compose
        fi
    fi
    
    $COMPOSE_CMD up --build
    
    echo ""
    echo -e "${GREEN}✓ Serviço finalizado${NC}"
}

# Função para rodar testes
run_tests() {
    echo ""
    echo -e "${BLUE}🧪 Executando testes...${NC}"
    
    $CONTAINER_CMD run --rm \
        --name bot-test \
        -e PYTHONUNBUFFERED=1 \
        -e IN_DOCKER=true \
        -e DISPLAY=:99 \
        -v "$(pwd)/account.txt:/app/account.txt:ro,z" \
        bot-mercadolivre:latest \
        python test_setup.py
    
    echo ""
    echo -e "${GREEN}✓ Testes finalizados${NC}"
}

# Função para shell interativo
run_shell() {
    echo ""
    echo -e "${BLUE}💻 Abrindo shell interativo...${NC}"
    
    $CONTAINER_CMD run --rm -it \
        --name bot-shell \
        -e PYTHONUNBUFFERED=1 \
        -e IN_DOCKER=true \
        -v "$(pwd):/app:z" \
        bot-mercadolivre:latest \
        /bin/bash
}

# Função para limpar containers e imagens
cleanup() {
    echo ""
    echo -e "${BLUE}🧹 Limpando containers e imagens...${NC}"
    
    $CONTAINER_CMD stop bot-mercadolivre 2>/dev/null || true
    $CONTAINER_CMD rm bot-mercadolivre 2>/dev/null || true
    $CONTAINER_CMD rmi bot-mercadolivre:latest 2>/dev/null || true
    
    echo -e "${GREEN}✓ Limpeza concluída${NC}"
}

# Menu principal
echo ""
echo "Escolha uma opção:"
echo "  1) Construir imagem"
echo "  2) Rodar bot (container único)"
echo "  3) Rodar com compose"
echo "  4) Rodar testes"
echo "  5) Shell interativo"
echo "  6) Limpar containers/imagens"
echo "  7) Sair"
echo ""

read -p "Opção: " choice

case $choice in
    1)
        build_image
        ;;
    2)
        build_image
        run_bot
        ;;
    3)
        run_compose
        ;;
    4)
        build_image
        run_tests
        ;;
    5)
        build_image
        run_shell
        ;;
    6)
        cleanup
        ;;
    7)
        echo "Até logo!"
        exit 0
        ;;
    *)
        echo -e "${RED}✗ Opção inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Operação concluída${NC}"
echo -e "${GREEN}========================================${NC}"
