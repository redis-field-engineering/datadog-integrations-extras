from codecs import open  # To use a consistent encoding
from os import path

from setuptools import setup

HERE = path.dirname(path.abspath(__file__))

# Get version info
ABOUT = {}
with open(path.join(HERE, "datadog_checks", "cloudsmith", "__about__.py")) as f:
    exec(f.read(), ABOUT)

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


def get_dependencies():
    dep_file = path.join(HERE, "requirements.in")
    if not path.isfile(dep_file):
        return []

    with open(dep_file, encoding="utf-8") as f:
        return f.readlines()


def parse_pyproject_array(name):
    import os
    import re
    from ast import literal_eval

    pattern = r"^{} = (\[.*?\])$".format(name)

    with open(os.path.join(HERE, "pyproject.toml"), "r", encoding="utf-8") as f:
        # Windows \r\n prevents match
        contents = "\n".join(line.rstrip() for line in f.readlines())

    array = re.search(pattern, contents, flags=re.MULTILINE | re.DOTALL).group(1)
    return literal_eval(array)


CHECKS_BASE_REQ = parse_pyproject_array("dependencies")[0]


setup(
    name="datadog-cloudsmith",
    version=ABOUT["__version__"],
    description="The Cloudsmith check",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="datadog agent cloudsmith check",
    # The project's main homepage.
    url="https://github.com/DataDog/integrations-extras",
    # Author details
    author="Ranjan Singh",
    author_email="rsingh@cloudsmith.io",
    # License
    license="BSD-3-Clause",
    # See https://pypi.org/classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.12",
    ],
    # The package we're going to ship
    packages=["datadog_checks.cloudsmith"],
    # Run-time dependencies
    install_requires=[CHECKS_BASE_REQ],
    extras_require={"deps": parse_pyproject_array("deps")},
    # Extra files to ship with the wheel package
    include_package_data=True,
)
