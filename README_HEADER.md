# Why you should pin your Python depnendencies (at least for development)

## Summary

This README contains a examples of how the dependencies of Python libraries change over time. 

The examples here are of: `fastapi`, `pandas`, `streamlit` `sphinx`, `requests`, and `poetry`.

> ⚠️ If you are a data scientist, *please* document your Python dependencies as well as your Python version when you run experiments.
> There are non-python dependencies to document, too, but this analysis does not cover that. Dockerfile's
> are very helpful for that, though.

## Background

Serious stress happens if you come back to some code you wrote months ago only to find you can't get it to run.

The biggest reason for this in the Python world is that the dependencies you were using back when you authored
your code have probably changed since that time.

I do *not* believe you should force consumers of your Python code/packages to install exact versions.

But you can give yourself the *option* to do so by committing a "lock file" to your repo and updating it
every once and a while.

You can generate a lock file a few different ways:

- pip: `pip freeze > requirements.txt`
- pip-tools: `pip-compile --output-file requirements.txt requirements.in`
- poetry
- pipenv

## How to reproduce(ish) these results

```bash
# install the python and non-python dependencies
pip install -r requirements.txt
brew install graphviz

# generate the dependency graphs for a library by downloading many versions of it
python generate_dependency_graph.py fastapi

# generate this README.md
python generate_readme.py
```

This works by fetching a list of all published versions of a given python package from the PyPI API.

For example, try visiting this link: https://pypi.org/pypi/fastapi/json

Then the script downloads a subset of the discovered versions and plots their dependency graphs.
