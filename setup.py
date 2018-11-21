#!/usr/bin/python
from setuptools import setup, find_packages
try:
    from pip._internal.req import parse_requirements
except:
    from pip.req import parse_requirements
from oshino.version import get_version

install_reqs = list(parse_requirements("requirements/release.txt", session={}))
ntest_reqs = list(parse_requirements("requirements/test.txt", session={}))

with open("README.md", "r") as f:
    desc = f.read()

setup(name="oshino",
      version=get_version(),
      long_description=desc,
      description="Metrics collector for Riemann",
      url="https://github.com/CodersOfTheNight/oshino",
      author="Šarūnas Navickas",
      author_email="zaibacu@gmail.com",
      license="MIT",
      packages=find_packages(),
      install_requires=[str(ir.req) for ir in install_reqs],
      test_suite="pytest",
      tests_require=[str(tr.req) for tr in test_reqs],
      setup_requires=["pytest-runner"],
      entry_points={
          "console_scripts": [
                "oshino = oshino.run:main"
          ]
      },
      classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
      ]
      )
