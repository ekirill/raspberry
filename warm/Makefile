CWD:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

migrate:
	PYTHONPATH=$(CWD) python3 ./repository/migrations.py

run-dev:
	/usr/local/bin/uvicorn --reload api:app --host 192.168.1.200
