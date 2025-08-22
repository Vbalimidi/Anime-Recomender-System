from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="MLOPS-2",
    version="0.1",
    author="Vidya Balimidi",
    packages=find_packages(),
    install_requires=requirements
)