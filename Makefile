.PHONY: lint
lint: pylint mypy bandit

.PHONY: pylint
pylint:
	pylint ./**/*.py

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports .

.PHONY: bandit
bandit:
	bandit -r .

.PHONY: test
test:
	python3 manage.py test
