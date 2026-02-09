# Makefile para facilitar comandos do bot

.PHONY: help build run test shell clean install dev

# Detecta Podman ou Docker
CONTAINER_CMD := $(shell command -v podman 2> /dev/null || echo docker)
COMPOSE_CMD := $(shell command -v podman-compose 2> /dev/null || echo "docker compose")

help: ## Mostra esta ajuda
	@echo "Bot Mercado Livre - Comandos Disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Container Runtime: $(CONTAINER_CMD)"

# ============================================
# Instalação e Setup
# ============================================

install: ## Instala dependências Python localmente
	pip install -r requirements.txt

setup: ## Configura o projeto (cria account.txt se não existir)
	@if [ ! -f account.txt ]; then \
		echo "Criando account.txt..."; \
		cp account.txt.example account.txt; \
		echo "⚠️  Edite account.txt com suas credenciais!"; \
	else \
		echo "✓ account.txt já existe"; \
	fi
	@mkdir -p outputs
	@echo "✓ Setup completo"

# ============================================
# Execução Local (sem container)
# ============================================

run-local: ## Executa o bot localmente (sem container)
	python run_bot.py

test-local: ## Executa testes localmente
	python test_setup.py

# ============================================
# Docker/Podman
# ============================================

build: ## Constrói a imagem Docker/Podman
	$(CONTAINER_CMD) build -t bot-mercadolivre:latest .

run: build ## Executa o bot em container
	$(CONTAINER_CMD) run --rm \
		--name bot-mercadolivre \
		-e PYTHONUNBUFFERED=1 \
		-e IN_DOCKER=true \
		-e DISPLAY=:99 \
		-v $(PWD)/outputs:/app/outputs:z \
		-v $(PWD)/account.txt:/app/account.txt:ro,z \
		bot-mercadolivre:latest

run-compose: ## Executa com docker-compose/podman-compose
	$(COMPOSE_CMD) up --build

test: build ## Executa testes em container
	$(CONTAINER_CMD) run --rm \
		--name bot-test \
		-e IN_DOCKER=true \
		-v $(PWD)/account.txt:/app/account.txt:ro,z \
		bot-mercadolivre:latest \
		python test_setup.py

shell: build ## Abre shell interativo no container
	$(CONTAINER_CMD) run --rm -it \
		--name bot-shell \
		-e IN_DOCKER=true \
		-v $(PWD):/app:z \
		bot-mercadolivre:latest \
		/bin/bash

# ============================================
# Limpeza
# ============================================

clean: ## Remove containers e imagens
	-$(CONTAINER_CMD) stop bot-mercadolivre 2>/dev/null
	-$(CONTAINER_CMD) rm bot-mercadolivre 2>/dev/null
	-$(CONTAINER_CMD) rmi bot-mercadolivre:latest 2>/dev/null
	@echo "✓ Limpeza concluída"

clean-outputs: ## Remove arquivos Excel gerados
	rm -f outputs/*.xlsx
	@echo "✓ Outputs limpos"

clean-all: clean clean-outputs ## Remove tudo (containers, imagens e outputs)
	@echo "✓ Limpeza completa"

# ============================================
# Desenvolvimento
# ============================================

dev: ## Executa em modo desenvolvimento (monta código como volume)
	$(CONTAINER_CMD) run --rm -it \
		--name bot-dev \
		-e PYTHONUNBUFFERED=1 \
		-e IN_DOCKER=true \
		-e DISPLAY=:99 \
		-v $(PWD):/app:z \
		bot-mercadolivre:latest \
		/bin/bash

logs: ## Mostra logs do container (se rodando em background)
	$(CONTAINER_CMD) logs -f bot-mercadolivre

ps: ## Lista containers em execução
	$(CONTAINER_CMD) ps -a | grep bot-mercadolivre || echo "Nenhum container bot-mercadolivre encontrado"

stats: ## Mostra estatísticas de recursos do container
	$(CONTAINER_CMD) stats bot-mercadolivre

# ============================================
# Atalhos úteis
# ============================================

.DEFAULT_GOAL := help
