from setuptools import find_packages, setup

setup(
    name="dataflux",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dataflux=launch:main",
        ],
    },
)
