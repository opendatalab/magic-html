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
            "common_html_extractor"
        ):
            return version_parts[1]
        else:
            raise ValueError(
                f"Invalid version tag {version}. Expected format is common_html_extractor-<version>-released."
            )
    except Exception as e:
        print(e)
        return "0.0.0"


requires = parse_requirements("requirements.txt")

setup(
    name="common_html_extractor",
    # version="0.1.3",
    version=get_version(),
    packages=["common_html_extractor"],
    install_requires=requires,
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)
# python setup.py sdist bdist_wheel
