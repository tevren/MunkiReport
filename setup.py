# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import munkireport
import subprocess

p = subprocess.Popen(["svnversion"], stdout=subprocess.PIPE)
(out, err) = p.communicate()
p.wait()
svnrev = filter(lambda x: x.isdigit(), out.strip().split(":")[-1])


setup(
    name='MunkiReport',
    version="%s.%s" % (munkireport.__version__, svnrev),
    description='Report viewer for Munki',
    author='Per Olofsson',
    author_email='per.olofsson@gu.se',
    url='http://code.google.com/p/munkireport/',
    license='Apache License 2.0',
    long_description="MunkiReport gathers Munki reports from your clients, showing you errors and current activity, as well as details for individual clients.",
    install_requires=[
        "TurboGears2 >= 2.1",
        "Babel >= 0.9.4",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        "repoze.what-quickstart >= 1.0",
        "tgext.admin >= 0.3.3",
        "genshi >= 0.6",
        "repoze.what.plugins.ini >= 0.2.2",
        "pexpect >= 2.4",
        "tgext.crud >= 0.3.9",
    ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'munkireport': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*.*',
                                 'public/*/*.*']},
    exclude_package_data = {'munkireport': ['.DS_Store']},
    message_extractors={'munkireport': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = munkireport.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
    zip_safe=False,
)
