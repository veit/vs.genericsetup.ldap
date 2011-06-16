# -*- coding: utf-8 -*-

from zope.interface import Interface

class ILDAPPlugin(Interface):
    """ Marker Interface for LDAPUserFolder for LDAP
    """

class IADPlugin(Interface):
    """ Marker Interface for LDAPUserFolder for AD
    """