import setuptools
import pyraid._version

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", 'r') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    # How you named your package folder (MyLib)
    name=pyraid._version.__package__,
    # Chose the same as "name"
    packages=setuptools.find_packages(),
    # Start with a small number and increase it with every change you make
    version=pyraid._version.__version__,
    license='GNU General Public License v3 (GPLv3)',
    # Give a short description about your library
    description="General purpose helper functions and classes for Python3 projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Type in your name
    author=pyraid._version.__author__,
    # Type in your E-Mail
    author_email='n8gr8gbln@gmail.com',
    # Provide either the link to your github or to your website
    url=f'https://github.com/nwithan8/{pyraid.__package__}',
    download_url=f'https://github.com/nwithan8/{pyraid.__package__}/archive/{pyraid._version.__version__}.tar.gz',
    # Keywords that define your package best
    keywords=[
        'Python',
        'Python3',
        'requests',
        'Unraid',
        'API',
        'Docker',
        'VM',
        'virtual machine',
        'control',
        'server'
    ],
    install_requires=requirements,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        # Define that your audience are developers
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Specify which python versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.7'
)
