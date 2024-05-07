# -*- coding:utf-8 -*-

from setuptools import setup
import subprocess


def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()

    requires = []

    for line in lines:
        if "http" in line:
            pkg_name_with_version = line.split("/")[-1].split("-")[0]
            requires.append(pkg_name_with_version)
        else:
            requires.append(line)

    return requires


def get_version():
    command = ["git", "describe", "--tags"]
    try:
        version = subprocess.check_output(command).strip()
        version_parts = version.split("-")
        if len(version_parts) > 1 and version_parts[0].startswith(
            "magic_html"
        ):
            return version_parts[1]
        else:
            raise ValueError(
                f"Invalid version tag {version}. Expected format is magic_html-<version>-released."
            )
    except Exception as e:
        print(e)
        return "0.0.0"


requires = parse_requirements("requirements.txt")

setup(
    name="magic_html",
    version=get_version(),
    packages=["magic_html", "magic_html.extractors"],
    package_data={"magic_html": ["mmltex/*.xsl"]},
    install_requires=requires,
    python_requires=">=3.8",
    zip_safe=False,
)
# python setup.py bdist_wheel
