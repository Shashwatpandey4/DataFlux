from setuptools import find_packages, setup

setup(
    name="dataflux",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "jinja2>=3.0.0",
        "websockets>=10.0",
        "python-multipart>=0.0.5",
    ],
    entry_points={
        "console_scripts": [
            "dataflux=src.main:main",
            "dataflux-start=src.main:start_command",
        ],
    },
)
