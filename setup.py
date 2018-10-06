"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='hyperwave',
    version='0.1',
    license='MIT',
    description='hyperwave research',

    author='David Zucker',
    author_email='david@programmableproduction.com',
    url='http://blog.programmableproduction.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['numpy', 'pandas', 'pytest-runner', 'attrs', 'pytest'],

    # entry_points={
    #     'console_scripts': [
    #         'tasks = tasks.cli:tasks_cli',
    #     ]
    # },
)