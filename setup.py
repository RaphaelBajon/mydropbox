from setuptools import setup, find_packages

setup(
    name="mydropbox",
    version="0.1.0",
    author="Raphaël Bajon",
    description="A library for managing UHM Ocean BGC Group Dropbox paths",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Ocean Science",
    ],
)
