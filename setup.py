from setuptools import *


setup(
    name='Grace',
    description='The Code Society community Bot',
    version='1.2.0',
    author='Code Society Lab',
    author_email='',
    python_require='>=3.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'python-dotenv',
        'coloredlogs',
        'logger',
        'sqlalchemy',
        'sqlalchemy-utils',
        'discord',
        'emoji',
        'nltk',
        'discord-pretty-help',
        'requests',
        'psycopg2'
    ],
    scripts=['scripts/grace'],
)
