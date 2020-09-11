from setuptools import setup, find_packages


setup(
    name='book-tools',
    version='0.0.1',
    url='https://github.com/kgpayne/book-tools.git',
    author='Ken Payne',
    author_email='me@kenpayne.co.uk',
    description='A collection of tools for processing books and book data.',
    packages=find_packages(),
    install_requires=['probablepeople==0.5.4'],
)
