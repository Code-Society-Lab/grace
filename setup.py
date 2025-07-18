from setuptools import setup, find_packages

setup(
    name='Grace',
    version='2.0.0',
    author='Code Society Lab',
    description='The Code Society community Bot',
    url="https://github.com/Code-Society-Lab/grace",
    project_urls={
        "Documentation": "https://github.com/Code-Society-Lab/grace/wiki",
        "Issue tracker": "https://github.com/Code-Society-Lab/grace/issues",
        "Discord server": "https://discord.gg/code-society-823178343943897088",
    },
    license="GNU General Public License v3.0",
    python_requires='>=3.10.0',

    packages=find_packages(),

    include_package_data=True,
    install_requires=[
        # For now we always want the latest version on github
        'grace-framework @ git+https://github.com/Code-Society-Lab/grace-framework.git@main',
        'emoji>=2.1.0',
        'nltk',
        'discord-pretty-help==2.0.4',
        'requests',
        'pillow',
        'geopy',
        'pytz',
        'tzdata',
        'timezonefinder',
        'pygithub',
        'googletrans==4.0.0-rc1',
        'openai==0.26.1',
        'apscheduler'
    ]
)
