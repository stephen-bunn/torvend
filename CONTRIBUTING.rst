============
Contributing
============

This document is to help you start development with this project.


Setup
-----
You can fork and clone ``torvend`` at the `GitHub <https://github.com/stephen-bunn/torvend>`_ repository.
You will also need to work inside a virtual environment while developing this project.
For this reason I recommend installing `pipenv <https://github.com/kennethreitz/pipenv>`_ for working with this project.

You can install the dependencies of the project by running the command ``pipenv --three install --dev`` at the root of the repository.
This should install all of the required dependencies for development.

---

You can run the project by creating a file (*main.py*) at the root of the repository.
Here you can import the ``torvend`` package and debug your changes by running the command ``pipenv run main.py``


Style Guides
------------
This project uses `flake8 <http://flake8.pycqa.org/en/latest/>`_ as its primary style guide.
