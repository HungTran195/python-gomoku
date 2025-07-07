#!/usr/bin/env python3
"""
Setup script for Python Gomoku Game
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='python-gomoku',
    version='2.0.0',
    description='A modern Gomoku (Five in a Row) game built with Django 5.3',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Original Author + Contributors',
    author_email='',
    url='https://github.com/yourusername/python-gomoku',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Django',
        'Framework :: Django :: 5.3',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='gomoku, game, django, ai, minimax, websocket',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/python-gomoku/issues',
        'Source': 'https://github.com/yourusername/python-gomoku',
        'Documentation': 'https://github.com/yourusername/python-gomoku#readme',
    },
    entry_points={
        'console_scripts': [
            'gomoku=manage:main',
        ],
    },
) 