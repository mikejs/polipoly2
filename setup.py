from setuptools import setup

setup(
    name='polipoly2',
    packages=['polipoly2'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask>=0.6',
                      'SQLAlchemy>=0.6.4',
                      'GeoAlchemy>=0.4.1',
                      'lxml>=2.2.8'])
