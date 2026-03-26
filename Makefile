PYTHON ?= .venv/bin/python

.PHONY: run-examples test

run-examples:
	$(PYTHON) scripts/run_examples.py

test:
	$(PYTHON) -m pytest

