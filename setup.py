from setuptools import setup, find_packages
import os

version = '1.1.0'

setup(name='vs.genericsetup.ldap',
      version=version,
      description="Extension for GenericSetup, support for LDAP and AD",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Zope Plone Python LDAP AD GenericSetup',
      author='Anne Walther / Alexander Loechel for IDG (http://www.immanuel.de)/ Veit Schiele (http://www.veit-schiele.de), Andreas Jung (www.zopyx.com)',
      author_email='awello@gmail.com / Alexander.Loechel@unibw.de / info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      url='http://svn.plone.org/svn/collective/collective.genericsetup.ldap',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.genericsetup'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.GenericSetup',
          'Products.PloneLDAP',
          # -*- If Products.PloneLDAP not work on Plone 2.5: -*-
          'Products.LDAPMultiPlugins',
          'Products.LDAPUserFolder',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
