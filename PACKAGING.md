# Instructions for packaging MetaWards

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
