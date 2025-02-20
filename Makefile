# -*- mode: Makefile -*-

.PHONY: dev_install install init test

install:
	echo "pip install --user ."

dev_install:
	pip install --editable .

init:
	pip install -r requirements

test:
	py.test tests

clean:
	-rm -rf cfgr.egg-info __pycache__
