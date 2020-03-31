# Instructions for packaging MetaWards

First, remember to update the version of MetaWards in the
code. We will automate this later, but for now you need to
update

* `setup.cfg` : Update the third line, `version = {VERSION}`
* `Makefile`  : Update the rule for `install-from-source`
* `src/metawards/__init__.py` : Update `__version__ = "{VERSION}"

Next (after committing these changes) create a Git tag using;

```
git tag -a v{VERSION} -m "Message"
```

e.g.

```
git tag -a v0.2.0b -m "Beta release of 0.2.0"
```

then push your tag to GitHub

```
git push --tags
```

## Creating the pip package

To create the pip package and upload to pypi type;

```
python3 -m pip install --user --upgrade setuptools wheel
```

Now run this command from the same directory where setup.py is located

```
python3 setup.py sdist bdist_wheel
```

Now ensure you have the latest version of twine installed

```
python3 -m pip install --user --upgrade twine
```

Next upload to pypi, using

```
python3 -m twine upload dist/*
```

Note you will need a username and password for pypi and to have
permission to upload code to this project.

