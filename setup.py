
from setuptools import setup, find_packages
import os.path
import re

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'microhttp_restful', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)


dependencies = [
    'microhttp',
    'sqlalchemy_dict >= 0.3.2',
    'webtest_docgen'
]


setup(
    name='microhttp-restful',
    version=package_version,
    author='Mahdi Ghanea.g',
    author_email='contact@meyti.ir',
    url='http://github.com/meyt/microhttp-restful',
    description='A tool-chain for create RESTful web applications.',
    long_description=open('README.rst').read(),
    install_requires=dependencies,
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
