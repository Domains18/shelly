from setuptools import setup, find_packages

setup(
    name="shelly",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Dependencies will be read from requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'shelly=shelly.main:main',
        ],
    },
    author="Your Name",
    description="A shell utility for managing development environments",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)
