##*********************
##* Makefile commands *
##*********************
##

.DEFAULT_GOAL := help


.PHONY: help
help:           ## show this help
	@sed -nE '/@sed/!s/##\s?//p' Makefile


.PHONY: run
run:            ## run script
	../venv/bin/python ./src/main.py


.PHONY: deploy
deploy:         ## deploy using ansible
	ansible-playbook --ask-vault-pass -i ../../infra/inventory.yml ./playbook.yml
