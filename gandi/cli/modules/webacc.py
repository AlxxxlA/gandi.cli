""" Webaccelerator commands module """

from gandi.cli.core.base import GandiModule


class Webacc(GandiModule):

    """ Module to handle CLI commands.

    $ gandi webacc list
    $ gandi webacc info
    $ gandi webacc create
    
    """

    @classmethod
    def list(cls, options=None):
        if not options:
            options =  {}
        return cls.call('hosting.rproxy.list', options)


    @classmethod
    def info(cls, id):
        return cls.call('hosting.rproxy.info', cls.usable_id(id))


    @classmethod
    def create(cls, options={}):
        return cls.call('hosting.rproxy.create', options)

    @classmethod
    def usable_id(cls, id):
        """ Retrieve id from input which can be hostname, vhost, id. """
        try:
            # id is maybe a hostname
            qry_id = cls.from_name(id)
            if not qry_id:
                # id is maybe an ip
                qry_id = cls.from_ip(id)
            if not qry_id:
                qry_id = cls.from_vhost(id)
        except Exception:
            qry_id = None

        if not qry_id:
            msg = 'unknown identifier %s' % id
            cls.error(msg)

        return qry_id


    @classmethod
    def from_name(cls, name):
        """Retrieve webacc id associated to a webacc name."""
        result = cls.list({})
        webaccs = {}
        for webacc in result:
            webaccs[webacc['name']] = webacc['id']
        return webaccs.get(name)


    @classmethod
    def from_ip(cls, ip):
        """Retrieve webacc id associated to a webacc ip"""
        result = cls.list({})
        gandi.echo('prout')
        webaccs = {}
        for webacc in result:
            for server in webacc['servers']:
                webaccs[server['ip']] = webacc['id']
        return webaccs.get(ip)


    @classmethod
    def from_vhost(cls, vhost):
        """Retrieve webbacc id associated to a webacc vhost"""
        # FIXME
        result = cls.list({})
        webaccs = {}
        for webacc in result:
            for vhost in webacc['vhosts']:
                webaccs[vhost['name']] = webacc['id']
                gandi.echo(vhost)
        return webaccs.get(vhost)