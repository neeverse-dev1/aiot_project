from setuptools import setup, find_packages

setup(
    name="aiot_project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "adafruit-circuitpython-dht",

    ],
)
