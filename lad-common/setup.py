import setuptools
import subprocess

from os import path, environ
from setuptools import find_packages
from pip._internal.req import parse_requirements


def get_requirements(name):
    install_reqs = parse_requirements(path.abspath(path.join("./requirements", name + ".txt")), session="hack")
    return [str(ir.req) for ir in install_reqs]


version = environ.get("CIRCLE_BUILD_NUM", None)

if version is None:
    git_out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE)
    revision = git_out.stdout
    version = f"0.0.dev" + revision.decode("utf-8").rstrip()
else:
    version = "0." + version + ".0"

setuptools.setup(
    name="lad_common",
    version=version,
    author="Andrey Maralin",
    author_email="a.a.maralin@gmail.com",
    description="A package with common functionality used in lad platform",
    url="https://github.com/amdrey-maralin/lad",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=get_requirements("production"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
