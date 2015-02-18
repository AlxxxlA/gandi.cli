""" Webaccelerator commands module """

from gandi.cli.core.base import GandiModule
from gandi.cli.modules.datacenter import Datacenter


class Webacc(GandiModule):

    """ Module to handle CLI commands.

    $ gandi webacc list
    $ gandi webacc info
    $ gandi webacc create
    $ gandi webacc delete
    $ gandi webacc probe
    $ gandi webacc backend
    $ gandi webacc vhost

    """

    @classmethod
    def list(cls, options=None):
        if not options:
            options = {}
        return cls.call('hosting.rproxy.list', options)

    @classmethod
    def info(cls, id):
        return cls.call('hosting.rproxy.info', cls.usable_id(id))

    @classmethod
    def create(cls, name, datacenter, backends, vhosts, algorithm,
               ssl_enable, zone_alter):
        datacenter_id_ = int(Datacenter.usable_id(datacenter))
        params = {
            'datacenter_id': datacenter_id_,
            'name': name,
            'lb': {'algorithm': algorithm},
            'override': True,
            'servers': backends,
            'vhosts': vhosts,
            'ssl_enable': ssl_enable,
            'zone_alter': zone_alter
        }
        cls.echo(params)
        result = cls.call('hosting.rproxy.create', params)
        cls.echo('Creating your webaccelerator %s' % params['name'])
        cls.display_progress(result)
        cls.echo('Your webaccelerator have been created')
        return result

    @classmethod
    def delete(cls, name):
        """ Delete a webaccelerator """
        result = cls.call('hosting.rproxy.delete', cls.usable_id(name))
        cls.echo('Deleting your rproxy named %s' % name)
        cls.display_progress(result)
        cls.echo('Rproxy have been deleted')
        return result

    @classmethod
    def backend_list(cls, options):
        """ List all servers used by webaccelerator """
        return cls.call('hosting.rproxy.server.list', options)

    @classmethod
    def backend_add(cls, name, backends):
        """ Add a backend into a webaccelerator """
        for backend in backends:
            oper = cls.call(
                'hosting.rproxy.server.create', cls.usable_id(name), backend)
            cls.echo('Adding backend into webaccelerator')
            cls.display_progress(oper)
            cls.echo('Backend added')
        return oper

    @classmethod
    def backend_remove(cls, ip):
        """ Remove a backend on a webaccelerator """
        params = {'ip': ip}
        server = cls.backend_list(params)[0]
        oper = cls.call('hosting.rproxy.server.delete', server['id'])
        cls.echo('Removing backend into webaccelerator')
        cls.display_progress(oper)
        cls.echo('Your backend have been removed')
        return oper

    @classmethod
    def vhost_list(cls):
        """ List all servers used by webaccelerator """
        return cls.call('hosting.rproxy.vhost.list')

    @classmethod
    def vhost_add(cls, resource, params):
        """ Add a vhost into a webaccelerator """
        oper = cls.call(
            'hosting.rproxy.vhost.create', cls.usable_id(resource), params)
        cls.echo('Adding your virtual host into %s' % resource)
        cls.display_progress(oper)
        cls.echo('Your virtual host habe been added')
        return oper

    @classmethod
    def vhost_remove(cls, name):
        """ Delete a vhost in a webaccelerator """
        oper = cls.call('hosting.rproxy.vhost.delete', name)
        cls.echo('Deleting your virtual host %s' % name)
        cls.display_progress(oper)
        cls.echo('Your virtual host have been removed')
        return oper

    @classmethod
    def probe(cls, resource, enable, disable, test, host, interval,
              http_method, http_response, threshold, timeout, url, window):
        """ Set a probe for a webaccelerator """
        params = {
            'host': host,
            'interval': interval,
            'method': http_method,
            'response': http_response,
            'threshold': threshold,
            'timeout': timeout,
            'url': url,
            'window': window
        }
        if enable:
            params['enable'] = True
        elif disable:
            params['enable'] = False
        if test:
            result = cls.call(
                'hosting.rproxy.probe.test', cls.usable_id(resource), params)
        else:
            result = cls.call(
                'hosting.rproxy.probe.update', cls.usable_id(resource), params)
            cls.display_progress(result)
        return result

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
        webaccs = {}
        for webacc in result:
            for server in webacc['servers']:
                webaccs[server['ip']] = webacc['id']
        return webaccs.get(ip)

    @classmethod
    def from_vhost(cls, vhost):
        """Retrieve webbacc id associated to a webacc vhost"""
        result = cls.list({})
        webaccs = {}
        for webacc in result:
            for vhost in webacc['vhosts']:
                webaccs[vhost['name']] = webacc['id']
        return webaccs.get(vhost)
