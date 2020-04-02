# Instructions for packaging MetaWards

First create a Git tag using;

```
git tag -a {VERSION} -m "Message"
```

e.g.

```
git tag -a 0.3.0b -m "Beta release of 0.3.0"
```

then push your tag to GitHub

```
git push --tags
```

The tag will be used by automatic versioning script to generate
the version numbers of the code. Building the package
(as happens below) will automatically update the _version.py
that is included in the package to tag versions.

## Creating the pip package

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

