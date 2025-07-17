DOCKER = docker
DOCKER_COMPOSE = ${DOCKER} compose
CONTAINER_ODOO = odoo
CONTAINER_DB = odoo-postgres
DB_NAME = odoo_development

help:
	@echo "Available targets"
	@echo "  start					Start compose"
	@echo "	 stop					Stop compose"
	@echo "  restart				Restart compose"
	@echo "  console				Odoo interactive console"
	@echo "  psql					PostgreSQL shell"
	@echo "  logs-odoo				Logs odoo container"
	@echo "  logs-db				Logs db container"
	@echo "  addon-<addon_name>	restart instance and upgrade addon"

start:
	$(DOCKER_COMPOSE) up -d

stop:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

console:
	$(DOCKER) exec -it $(CONTAINER_ODOO) odoo shell --db_host=$(CONTAINER_DB) -d $(DB_NAME) -r $(CONTAINER_ODOO) -w $(CONTAINER_ODOO)

psql:
	$(DOCKER) exec -it $(CONTAINER_DB) psql -U $(CONTAINER_ODOO) -d $(DB_NAME)

logs-odoo:
	$(DOCKER_COMPOSE) logs -f $(CONTAINER_ODOO)

logs-db:
	$(DOCKER_COMPOSE) logs -f $(CONTAINER_DB)

logs:
	@echo "Usage: make logs-odoo or make logs-db"

define upgrade_addon
	$(DOCKER) exec -it $(CONTAINER_ODOO) odoo --db_host=$(CONTAINER_DB) -d $(DB_NAME) -r $(CONTAINER_ODOO) -w $(CONTAINER_ODOO) -u $(1) --no-http
endef

addon-%: restart
	$(call upgrade_addon,$*)

PHONY: start stop restart console psql logs odoo db
