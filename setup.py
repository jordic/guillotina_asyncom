# -*- coding: utf-8 -*-
from setuptools import Extension
from setuptools import find_packages
from setuptools import setup


long_description = open("README.md").read() + "\n"
changelog = open("CHANGELOG.md").read()
found = 0
for line in changelog.splitlines():
    if len(line) > 15 and line[-1] == ")" and line[-4] == "-":
        found += 1
        if found >= 20:
            break
    long_description += "\n" + line


long_description += """

...

You are seeing a truncated changelog.

You can read the `changelog file <https://github.com/plone/guillotina/blob/master/CHANGELOG.rst>`_
for a complete list.

"""

setup(
    name="guillotina_asyncom",
    python_requires=">=3.7.0",
    version=open("VERSION").read().strip(),
    description="Guillotina Postgresql integration",  # noqa
    long_description=long_description,
    keywords=["asyncio", "REST", "Framework", "transactional", "asgi", "postgresql", "sqlalchemy"],
    author="Jordi Collell",
    author_email="jordic@gmail.com",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/jordic/guillotina_asyncom",
    license="BSD",
    setup_requires=["pytest-runner"],
    zip_safe=False,
    include_package_data=True,
    package_data={"": ["*.txt", "*.rst"]},
    packages=find_packages(),
    install_requires=[
        "guillotina",
        "asyncom",
    ],
    extras_require={
        "test": [
            "pytest>=3.8.0<=5.0.0",
            "docker",
            "backoff",
            "psycopg2-binary",
            "pytest-asyncio>=0.10.0",
            "pytest-cov",
            "coverage>=4.0.3",
            "pytest-docker-fixtures",
            "pytest-rerunfailures<=7.0",
            "async-asgi-testclient~=1.2.0",
        ],
    }
)
