.PHONY: all setup test test-backend test-frontend smoke start clean

all: setup test

setup:
	@echo "Setting up NetMirage backend and frontend dependencies..."
	python -m venv app_build/backend/.venv
	./app_build/backend/.venv/bin/pip install -r app_build/backend/requirements.txt
	cd app_build/frontend && npm install

test: test-backend test-frontend smoke

test-backend:
	@echo "Running backend test suite (pytest)..."
	./app_build/backend/.venv/bin/python -m pytest app_build/backend/tests -v

test-frontend:
	@echo "Running frontend test suite (vitest) and build check..."
	cd app_build/frontend && npm test && npm run build

smoke:
	@echo "Running live programmatic smoke test..."
	./app_build/backend/.venv/bin/python app_build/backend/tests/live_smoke_test.py

start:
	@bash app_build/start_netmirage.sh

clean:
	rm -rf app_build/frontend/dist app_build/backend/.pytest_cache netmirage.db
