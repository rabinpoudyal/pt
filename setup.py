
from setuptools import setup, find_packages 

from pt.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='pt-cli',
    version=VERSION,
    description='It uses an pivotal tracker api and does lot of cool stuffs like creating tickets.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Rabin Poudyal',
    author_email='rabinpoudyal1995@gmail.com',
    url='https://github.com/rabinpoudyal/pt',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'pt': ['templates/*']},
    include_package_data=True,
    install_requires=[
        "cement==3.0.4",
        "jinja2",
        "colorlog",
        "requests",
        "enquiries",
        "pyyaml",
        "rich",
        "tabulate",
    ],
    entry_points="""
        [console_scripts]
        pt = pt.main:main
    """,
)
