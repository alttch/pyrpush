__version__ = "0.1.6"

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrpush",
    version=__version__,
    author='Altertech Group',
    author_email="pr@altertech.com",
    description="Push client for Roboger event pager",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/alttch/pyrpush",
    packages=setuptools.find_packages(),
    license='Apache License 2.0',
    install_requires=['requests'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Communications",
    ),
)
