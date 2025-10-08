# Makefile for Raspberry Pi GPIO Control Application

.PHONY: help install test test-cov test-unit test-integration clean lint format

help:
	@echo "可用命令："
	@echo "  make install          - 安装所有依赖"
	@echo "  make install-dev      - 安装开发依赖"
	@echo "  make test             - 运行所有测试"
	@echo "  make test-cov         - 运行测试并生成覆盖率报告"
	@echo "  make test-unit        - 只运行单元测试"
	@echo "  make test-integration - 只运行集成测试"
	@echo "  make test-watch       - 监控模式运行测试"
	@echo "  make lint             - 运行代码检查"
	@echo "  make format           - 格式化代码"
	@echo "  make clean            - 清理生成的文件"
	@echo "  make run              - 运行应用"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

test-unit:
	pytest tests/ -m "not integration" -v

test-integration:
	pytest tests/ -m integration -v

test-watch:
	pytest-watch

test-verbose:
	pytest -vv -s

lint:
	flake8 app tests
	pylint app

format:
	black app tests
	isort app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build

run:
	python run.py

sync:
	./synctopi.sh
