from setuptools import setup, find_packages

# Read version from __init__.py
version = {}
with open("cloaksmith/__init__.py") as f:
    exec(f.read(), version)

setup(
    name='cloaksmith',
    version=version["__version__"],
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'Click',
        'python-dotenv',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'cloaksmith = cloaksmith.cli:cli',
        ],
    },
)
