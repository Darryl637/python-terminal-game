test:
	python -m pytest --cov-report=html --cov=src
typecheck:
	python -m mypy