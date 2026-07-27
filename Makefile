.PHONY: test build clean install

test:
	pytest tests/ -v

build:
	pip install build
	python -m build

install:
	pip install -e .

clean:
	rm -rf dist/ build/ *.egg-info
	rm -rf .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
