# Simple targets for common tasks
# .PHONY: run test lint build

start-server:
	cd backend && uv run fastapi dev app/main.py

test:
	cd backend && uv run pytest

jsonserver:
	cd frontend && npx json-server --watch db.json --host 0.0.0.0 --port 3000

start-ui:
	cd frontend && npm start
# lint:
# 	flake8 src/

# build:
# 	python setup.py sdist bdist_wheel
