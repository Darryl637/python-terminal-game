test:
	python -m pytest --cov-report=html --cov=game
typecheck:
	python -m mypy