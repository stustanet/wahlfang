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
	# a bit hacky due to the manage.py script now living in the main module but it werks, meh ...
	PYTHONPATH="${PYTHONPATH}:$(pwd)" WAHLFANG_DEBUG=True python3 wahlfang/manage.py test

.PHONY: package
package:
	python3 -m build