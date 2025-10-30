Installation
============

This document explains how to install the **fastapi-async-storages** package.
Note that you can use any package manager you prefer, such as `uv`, `pip`, or others.

Prerequisites
-------------
- Python 3.12 or higher
- A package manager like `uv` installed (see https://astral.sh/uv/ for more info)

Installation with uv
--------------------

You can install the package using `uv`:

.. code-block:: bash

    uv add fastapi-async-storages
    # for s3 support:
    uv add fastapi-async-storages[s3]

.. important::

    If you need **image support** (eg: :class:`~async_storages.StorageImage`),
    make sure to install the `Pillow` library.

Or, to install from source:

.. code-block:: bash

    git clone https://github.com/stabldev/fastapi-async-storages.git
    cd fastapi-async-storages
    uv sync --all-extras

Verify installation
-------------------

You can verify the package installation by importing it:

.. code-block:: python

    import async_storages
    print(async_storages.__version__)
