.PHONY: build dist redist install install-from-source clean uninstall

build:
	CYTHONIZE=1 python setup.py build

dist:
	CYTHONIZE=1 python setup.py sdist bdist_wheel

redist: clean dist

install:
	CYTHONIZE=1 pip install .

install-from-source: dist
	pip install dist/metawards-0.2.0.tar.gz

clean:
	$(RM) -r build dist
	$(RM) -r src/metawards/*.c
	git clean -fdX

uninstall:
	pip uninstall metawards
