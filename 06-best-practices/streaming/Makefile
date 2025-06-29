test:
	pytest tests/

integration_test: test
	@bash -c "/workspaces/mlops-zoomcamp/06-best-practices/streaming/integration-tests/run.sh"	

quality_checks:
	isort .
	black .
	pylint --recursive=y .

build: quality_checks test integration_test
	echo run