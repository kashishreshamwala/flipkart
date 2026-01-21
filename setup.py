from setuptools import find_packages, setup
from typing import List

def get_requirements() -> list[str]:
    """
    This function will return list of requiremnets
    """

    requirement_list : List[str] = []
    """
    Write a code to read requirements.txt file and append each reuirements in requirement_list variable.
    """

    return requirement_list

setup(
    name = "flipkart",
    version = "0.0.1",
    author = "Kashish-Reshamwala",
    author_email = "kash7405@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements()

)