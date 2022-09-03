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
    version='2.2.0',
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
        'discord>=2.0',
        'emoji',
        'nltk',
        'discord-pretty-help==1.3.4',
        'requests',
        'pillow',
        'geopy',
        'pytz',
        'timezonefinder',
        'mypy',
    ],
    scripts=['scripts/grace'],
)

after_install()
