"""
build configuration
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="UTF-8") as f:
    long_description = f.read()
VERSION = "0.0.1.1"
setup(
    name="ysh",
    version=VERSION,
    author="Avi",
    description="A basic shell interface that can execute Unix commands",
    url="https://github.com/zenilist/tsh",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    keywords=["python", "terminal"],
    entry_points={
        "console_scripts": [
            "ysh = app.ysh:main",
        ]
    },
    install_requires=[
        "sshkeyboard",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)
