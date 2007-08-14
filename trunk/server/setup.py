from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='Forlater',
    version="0.8.5",
    #description="",
    #author="",
    #author_email="",
    #url="",
    install_requires=["Pylons>=0.9.5"],
    packages=find_packages(),
    package_data={
        'forlater': ['i18n/*/LC_MESSAGES/*.mo'],
        '': ['public/*.*', 'templates/*.*', 'public/images/*.*', 'public/js/*.*'],
    },
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
    [paste.app_factory]
    main=forlater:make_app
    [paste.app_install]
    main=pylons.util:PylonsInstaller
    """,
)
