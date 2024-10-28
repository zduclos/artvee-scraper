build: dependencies
	python setup.py sdist bdist_wheel

clean:
	rm -rf build dist .coverage .pytest_cache .mypy_cache *.egg-info
	find artvee_scraper tests \( -name "*.py[co]" -o -name __pycache__ -o -name "*.egg-info" \) -exec rm -rf {} +
	$(MAKE) -C docs clean

test: dependencies
	coverage run --source=artvee_scraper -m pytest -rP -v tests && coverage report -m

format: dependencies
	python -m black artvee_scraper

lint: dependencies
	python -m mypy --install-types artvee_scraper
	python -m mypy artvee_scraper

docs: dependencies
	$(MAKE) -C docs html

dependencies:
	pip install -r requirements.txt

.PHONY: build clean test dependencies
