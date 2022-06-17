from setuptools import *


def after_install():
    try:
        import nltk
        nltk.download('vader_lexicon')
    except ModuleNotFoundError:
        print("nltk module not properly installed")


setup(
    name='Grace',
    description='The Code Society community Bot',
    version='2.1.0',
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
        'pillow',
        'geopy',
        'pytz',
        'timezonefinder',
    ],
    scripts=['scripts/grace'],
)

after_install()
