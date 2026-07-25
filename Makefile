test:
	python -m pytest --cov=src --cov-report=html
typecheck:
	mypy --config-file mypy.ini .

prod:
	python main.py

venv:
	python -m venv venv

activate:
	venv\Scripts\activate.bat

freeze:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt


