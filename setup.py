from setuptools import setup, find_packages, setup
from typing import List


requirement_list: List[str] = []

filepath = 'requirements.txt'
def read_requirements():

    try:
        """Read the requirements from a file and return a list of packages."""
        with open(filepath, 'r') as file:
            lines=file.readlines()
            for line in lines:
                requirement=line.strip()
                if requirement and requirement!='-e .':
                    requirement_list.append(requirement)
    except FileNotFoundError:
        print(f"Error: The file {filepath} was not found.")
    return requirement_list
    

#print(read_requirements())

setup(
    name='Network_Security',
    version='0.0.1',
    author='Ankush Singh',
    author_email="singhankush06@gmail.com",
    packages=find_packages(),
    install_requires=read_requirements(),
    description='A package for Network Security',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
