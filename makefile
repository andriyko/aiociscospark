venv:
	. .venv/bin/activate

lint:
	flake8 .

test:
	py.test -s -vv --cov aiociscospark --cov-report term-missing

build:
	python setup.py sdist bdist_wheel

upload:
	twine upload dist/*
