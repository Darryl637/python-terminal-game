test:
	python -m pytest --cov-report=html --cov=src
typecheck:
	python -m mypy
dev:
	python -m reloadium run main.py
prod:
	python main.py