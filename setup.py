#!/usr/bin/python
# -*- coding: UTF-8 -*-
from setuptools import setup
from pip.req import parse_requirements

from oshino.version import get_version

install_reqs = list(parse_requirements("requirements/release.txt", session={}))
test_reqs = list(parse_requirements("requirements/test.txt", session={}))

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
      packages=["oshino", "oshino.core", "oshino.agents"],
      install_requires=[str(ir.req) for ir in install_reqs],
      test_suite="pytest",
      tests_require=[str(tr.req) for tr in test_reqs],
      setup_requires=["pytest-runner"],
      entry_points={'console_scripts': ['oshino = oshino.run:main'
                                        ]
                    }
      )
