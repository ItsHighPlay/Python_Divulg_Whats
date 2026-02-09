#!/bin/bash

# Script de verificação rápida do projeto

echo "╔════════════════════════════════════════╗"
echo "║   Bot Mercado Livre - Verificação    ║"
echo "╚════════════════════════════════════════╝"
echo ""

check_mark="✓"
cross_mark="✗"
warning="⚠"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

errors=0
warnings=0

# Função para verificar arquivo
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}${check_mark}${NC} $2"
    else
        echo -e "${RED}${cross_mark}${NC} $2 (arquivo não encontrado)"
        ((errors++))
    fi
}

# Função para verificar diretório
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}${check_mark}${NC} $2"
    else
        echo -e "${YELLOW}${warning}${NC} $2 (diretório não encontrado)"
        ((warnings++))
    fi
}

# Verificar arquivos principais
echo "📄 Arquivos Principais:"
check_file "bot.py" "Bot original"
check_file "bot_integrated.py" "Bot integrado"
check_file "affiliate.py" "Módulo de afiliados"
check_file "whatsapp_sender.py" "Módulo WhatsApp"
check_file "run_bot.py" "Script principal"
echo ""

# Verificar utilitários
echo "🔧 Utilitários:"
check_file "utils/support.py" "Funções auxiliares"
check_file "utils/environment.py" "Detecção de ambiente"
check_file "test_setup.py" "Testes de configuração"
echo ""

# Verificar Docker/Podman
echo "🐳 Containerização:"
check_file "Dockerfile" "Dockerfile"
check_file "docker-compose.yml" "Docker Compose"
check_file "run-podman.sh" "Script Linux/macOS"
check_file "run-podman.bat" "Script Windows"
check_file "Makefile" "Makefile"
echo ""

# Verificar ChromeDriver
echo "🚗 ChromeDriver:"
check_dir "utils/chromedriver-linux64" "ChromeDriver Linux"
check_file "utils/chromedriver-linux64/chromedriver" "Executável Linux"
check_dir "utils/chromedriver-win64" "ChromeDriver Windows"
echo ""

# Verificar configuração
echo "⚙️  Configuração:"
if [ -f "account.txt" ]; then
    # Verifica se está configurado
    if grep -q "seu_email@exemplo.com" account.txt 2>/dev/null; then
        echo -e "${YELLOW}${warning}${NC} account.txt (use credenciais reais)"
        ((warnings++))
    else
        login=$(grep "login = " account.txt | cut -d'=' -f2 | tr -d ' ')
        if [ -n "$login" ]; then
            echo -e "${GREEN}${check_mark}${NC} account.txt (configurado)"
        else
            echo -e "${YELLOW}${warning}${NC} account.txt (vazio)"
            ((warnings++))
        fi
    fi
else
    echo -e "${RED}${cross_mark}${NC} account.txt (não encontrado)"
    ((errors++))
fi

check_file "requirements.txt" "Dependências Python"
check_file "account.txt.example" "Template de credenciais"
check_file ".env.example" "Template de variáveis"
echo ""

# Verificar documentação
echo "📚 Documentação:"
check_file "README.md" "README principal"
check_file "MANUAL_USO.md" "Manual de uso"
check_file "PODMAN_GUIDE.md" "Guia Docker/Podman"
check_file "QUICKSTART.md" "Guia rápido"
check_file "CHANGELOG.md" "Log de mudanças"
echo ""

# Verificar outputs
echo "📁 Diretórios:"
check_dir "outputs" "Diretório de saída"
check_dir "utils" "Utilitários"
echo ""

# Verificar dependências Python
echo "🐍 Dependências Python:"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}${check_mark}${NC} Python $python_version"
    
    # Verifica se tem pip
    if command -v pip3 &> /dev/null; then
        echo -e "${GREEN}${check_mark}${NC} pip $(pip3 --version | cut -d' ' -f2)"
    else
        echo -e "${RED}${cross_mark}${NC} pip não encontrado"
        ((errors++))
    fi
else
    echo -e "${RED}${cross_mark}${NC} Python 3 não encontrado"
    ((errors++))
fi
echo ""

# Verificar container runtime
echo "🐳 Container Runtime:"
if command -v podman &> /dev/null; then
    echo -e "${GREEN}${check_mark}${NC} Podman $(podman --version | cut -d' ' -f3)"
elif command -v docker &> /dev/null; then
    echo -e "${GREEN}${check_mark}${NC} Docker $(docker --version | cut -d' ' -f3 | tr -d ',')"
else
    echo -e "${YELLOW}${warning}${NC} Nem Podman nem Docker encontrados (opcional)"
    ((warnings++))
fi
echo ""

# Resumo
echo "════════════════════════════════════════"
if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo -e "${GREEN}✓ Tudo pronto para usar!${NC}"
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Configure account.txt com suas credenciais"
    echo "   2. Execute: python run_bot.py"
    echo "   3. Ou com container: ./run-podman.sh"
elif [ $errors -eq 0 ]; then
    echo -e "${YELLOW}⚠  $warnings avisos encontrados${NC}"
    echo ""
    echo "💡 Revise os avisos acima antes de continuar"
else
    echo -e "${RED}✗ $errors erros e $warnings avisos encontrados${NC}"
    echo ""
    echo "❌ Corrija os erros acima antes de continuar"
    exit 1
fi

echo "════════════════════════════════════════"
echo ""
echo "📖 Documentação:"
echo "   - README.md - Visão geral"
echo "   - QUICKSTART.md - Início rápido"
echo "   - MANUAL_USO.md - Guia completo"
echo "   - PODMAN_GUIDE.md - Uso com containers"
echo ""
