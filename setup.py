from setuptools import setup
from setuptools import find_packages


version = '1.0.0'

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name = "osprey",
    version=version,
    description='Vulbox PoC-framework',
    long_description='osprey is a vulnerability detecting tool for security tester.',
    author='Cody Shi',
    author_email='cody.shi@tophant.com',
    url='http://www.vulbox.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
