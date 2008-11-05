# -*- coding: utf-8 -*-
# $LastChangedBy$ - $LastChangedDate$ - $Revision$

from StringIO import StringIO
from logging import getLogger
from ldap import SERVER_DOWN
from zope.interface import implements

from Products.LDAPMultiPlugins.LDAPMultiPlugin import manage_addLDAPMultiPlugin
from Products.LDAPMultiPlugins.ActiveDirectoryMultiPlugin import manage_addActiveDirectoryMultiPlugin

# if PloneLDAP isn't installed
try:
    from Products.PloneLDAP.factory import manage_addPloneActiveDirectoryMultiPlugin
    from Products.PloneLDAP.factory import manage_addPloneLDAPMultiPlugin
except:
    manage_addPloneActiveDirectoryPlugin = None
    manage_addPloneLDAPMultiPlugin = None

from xml.dom.minidom import parseString

try:
    from Products.GenericSetup.utils import PageTemplateResource
except ImportError: # BBB
    from Products.PageTemplates.PageTemplateFile import PageTemplateFile as PageTemplateResource

ldap_props = ['_login_attr',
              '_uid_attr', 
              '_rdnattr',
              'users_base',
              'users_scope',
              '_local_groups',
              '_implicit_mapping',
              'groups_base',
              'groups_scope',
              '_binduid',
              '_bindpwd',
              '_binduid_usage',
              'read_only',
              '_user_objclasses',
              '_pwd_encryption',
              '_roles']

_FILENAME = 'ldap_plugin.xml'

update = True

class LDAPPluginExportImport:
    """In- and Exporter for LDAP-PAS-Plugin
    """

    def exportData(self, context, out):
        template = PageTemplateResource('xml/%s' % _FILENAME, globals()).__of__(context.getSite())
        info = self._getExportInfo(context)
        if info:
            context.writeDataFile('%s' % _FILENAME,template(info=info),'text/xml')
            print >> out , "GenericSetup Configuration for ldap exported"

    def getTypeStr(self, value):
        val_type = 'str'
        if type(value) == type([]):
            val_type = 'list'
        elif type(value) == type(23):
            val_type = 'int'
        return val_type 
        
    def _getExportInfo(self, context):
        info = []
        portal = context.getSite()
        mt = getattr(portal, 'acl_users')
        for obj in mt.objectValues():
            if obj.meta_type in ['Plone LDAP plugin','LDAP Multi Plugin','Plone Active Directory plugin','ActiveDirectory Multi Plugin']:
                interfaces = []
                for p_info in obj.plugins.listPluginTypeInfo():
                    interface = p_info['interface']
                    actives = obj.plugins.listPlugins(interface)
                    act_ids = [x[0] for x in actives]
                    if obj.getId() in act_ids:
                        interfaces.append(p_info['id'])
                    
                c_info = {'meta_type': obj.meta_type, 'interfaces': interfaces, 'properties':[], 'schema':[], 'servers':[], 'id': obj.getId(), 'title': obj.title}
                uf = getattr(obj, 'acl_users')
                for prop in ldap_props:
                    value = uf.getProperty(prop)
                    val_type = self.getTypeStr(value)
                    if val_type != 'list':
                        value = [value]
                    c_info['properties'].append({'id': prop, 'type': val_type, 'value': value})
                for server in uf.getServers():
                    c_server = {'content':[]}
                    for key in server.keys():
                        c_server['content'].append({'id': key, 'value': server[key], 'type': self.getTypeStr(server[key])})
                    c_info['servers'].append(c_server)
                schema = uf.getSchemaConfig()
                for key in schema.keys():
                    a_item = {'id': key, 'content': [] }
                    for subkey in schema[key]:
                        s_item = {'id': subkey, 'value': schema[key][subkey], 'type': self.getTypeStr(schema[key][subkey])}
                        a_item['content'].append(s_item)
                    c_info['schema'].append(a_item)
                info.append(c_info)

        return info

    def importData(self, context, out):
        logger = context.getLogger('ldapsettings')
        xml = context.readDataFile(_FILENAME)
        if xml is None:
            logger.info('Nothing to import.')
            return
                   
        portal = context.getSite()
        pas = getattr(portal, 'acl_users')
        dom = parseString(xml)
        root = dom.documentElement
            
        for plugin in root.getElementsByTagName('ldapplugin'):
            self.extractData(plugin, pas, out)
            
    def extractData(self, root, pas, out):
        plug_id = str(root.getAttribute('id'))
        plug_title = root.getAttribute('title')
        plug_type = root.getAttribute('meta_type')
        plug_update = (root.getAttribute('update') == 'True')
        settings = {}
        interfaces = []
        for iface in root.getElementsByTagName('interface'):
            interfaces.append(iface.getAttribute('value'))
            
        for prop in root.getElementsByTagName('property'):
            type = prop.getAttribute('type')
            values = []
            for v in prop.getElementsByTagName('item'):
                values.append(v.getAttribute('value'))
            id = prop.getAttribute('id')
            if type == 'list': 
                value = values
            else: 
                value = values[0]
            if type == 'int':
                value = int(value)
            settings[id] = value 
        schema = {}
        for schemanode in root.getElementsByTagName('schema'):
             for attr in schemanode.getElementsByTagName('attr'):
                 c_id = attr.getAttribute('id')
                 c_attr = {}
                 for item in attr.getElementsByTagName('item'):
                     c_attr[item.getAttribute('id')] = item.getAttribute('value')
                 schema[c_id] = c_attr
        servers = []
        for server in root.getElementsByTagName('server'):
            c_server = {'update': (server.getAttribute('update') == 'True'),
                        'delete': (server.getAttribute('delete') == 'True')} 
            for item in server.getElementsByTagName('item'):
                value = item.getAttribute('value')
                type = item.getAttribute('type')
                id = item.getAttribute('id')
                if type == 'int':
                    value = int(value)
                c_server[id] = value
            servers.append(c_server) 
        
        adder = None    
        # use PloneLDAP    
        if (plug_type == 'Plone LDAP plugin') or ((plug_type == 'LDAP Multi Plugin') and (update)) :
            adder = manage_addPloneLDAPMultiPlugin
        elif (plug_type == ' Plone Active Directory plugin') or ((plug_type == 'ActiveDirectory Multi Plugin') and (update)) :
            adder = manage_addPloneActiveDirectoryMultiPlugin
            
        # use LDAPMultiPlugin
        elif (plug_type == 'LDAP Multi Plugin') and (not update):
            adder = manage_addLDAPMultiPlugin
        elif (plug_type == 'ActiveDirectory Multi Plugin') and (not update): 
            adder = manage_addActiveDirectoryMultiPlugin 
        # non LDAP Plugin Found
        if not adder:
            print >> out, "missing product for %s " % plug_type
        
        if plug_update and (plug_id in pas.objectIds()):
            pas.manage_delObjects(ids=[plug_id])   
        if plug_id not in pas.objectIds():
            try:
                adder(
                    self = pas,
                    id = plug_id,
                    title = plug_title,
                    LDAP_server = servers[0]['host'],
                    login_attr = settings['_login_attr'],
                    uid_attr = settings['_uid_attr'],
                    users_base = settings['users_base'],
                    users_scope = settings['users_scope'],
                    roles = settings['_roles'],
                    groups_base = settings['groups_base'],
                    groups_scope = settings['groups_scope'],
                    binduid = settings['_binduid'],
                    bindpwd = settings['_bindpwd'],
                    binduid_usage = settings['_binduid_usage'],
                    rdn_attr = settings['_rdnattr'],
                    local_groups = settings['_local_groups'],
                    use_ssl = servers[0]['protocol'] == 'ldaps',
                    encryption = settings['_pwd_encryption'],
                    read_only = settings['read_only'],
                )
                obj = getattr(pas, plug_id)
                obj.manage_activateInterfaces(interfaces)
                print >> out, "LDAP-plugin added: %s." % plug_id
            except SERVER_DOWN:
                print >> out, "LDAP-server down (%s)." % plug_id
            
        if len(servers) > 1:
            plugin = getattr(pas, plug_id)
            folder = plugin.acl_users
            existing_hosts = [server['host'] for server in folder.getServers()]
            for server in servers: 
                if (server['update'] or server['delete']) and server['host'] in existing_hosts:
                    folder.manage_deleteServers(position_list=[existing_hosts.index(server['host'])])
                if server['host'] not in existing_hosts:
                    folder.manage_addServer(host=server['host'], 
                        use_ssl = (server['protocol'] == 'ldaps'),
                        port=server['port'], 
                        conn_timeout=server['conn_timeout'], 
                        op_timeout=server['op_timeout'])


def exportLDAPSettings(context):
    exporter = LDAPPluginExportImport()
    out = StringIO() 
    exporter.exportData(context, out)
    logger = context.getLogger('ldapsettings')
    logger.info(out.getvalue())
         
def importLDAPSettings(context):
    importer = LDAPPluginExportImport()
    out = StringIO() 
    importer.importData(context, out)
    logger = context.getLogger('ldapsettings')
    logger.info(out.getvalue())
