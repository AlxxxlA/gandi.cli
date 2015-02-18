""" Webaccelerator namespace commands. """

import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import (
    output_generic, output_list, output_json, output_sub_generic
)
from gandi.cli.core.params import (
    pass_gandi, BACKEND, DATACENTER, WEBACC_NAME, WEBACC_VHOST_NAME
)


@cli.command()
@click.option('--limit', help="Limit the number of results", default=100,
              show_default=True)
@click.option('--format', type=click.Choice(['json', 'pretty-json']),
              required=False, help="Choose the output format")
@pass_gandi
def list(gandi, limit, format):
    """List webaccelerator"""
    options = {
        'items_per_page': limit,
    }

    result = gandi.webacc.list(options)
    if not format:
        output_keys = ['name', 'state', 'ssl']

        for num, webacc in enumerate(result):
                webacc['ssl'] = 'Disable' if webacc['ssl_enable'] is False else 'Enabled'
                output_generic(gandi, webacc, output_keys, justify=14)
                gandi.echo('Vhosts :')
                for num, vhost in enumerate(webacc['vhosts']):
                    output_vhosts = ['vhost', 'ssl']
                    vhost['vhost'] = vhost['name']
                    vhost['ssl'] = 'Disable' if vhost['cert_id'] is None else 'Enabled'
                    output_sub_generic(gandi, vhost, output_vhosts,
                                       justify=14)
                    if not num:
                        gandi.separator_sub_line('-', 2)
                gandi.echo('Servers :')
                for num, server in enumerate(webacc['servers']):
                    ip = gandi.ip.info(server['ip'])
                    iface = gandi.iface.info(ip['iface_id'])
                    server['name'] = gandi.iaas.info(iface['vm_id'])
                    ['hostname']
                    output_servers = ['name', 'ip', 'port', 'state']
                    output_sub_generic(gandi, server, output_servers,
                                       justify=14)
                    if num:
                        gandi.separator_sub_line('-', 2)
                if not num:
                    gandi.separator_line('-', 4)
    elif format:
        output_json(gandi, format, result)
    return result


@cli.command()
@click.option('--format', type=click.Choice(['json', 'pretty-json']),
              required=False, help="Choose the output format")
@click.argument('resource', type=WEBACC_NAME)
@pass_gandi
def info(gandi, resource, format):
    """ Dislay information about a webaccelerator """
    result = gandi.webacc.info(resource)
    if not format:
        output_base = {
            'name': result['name'],
            'algorithm': result['lb']['algorithm'],
            'datacenter': result['datacenter']['name'],
            'state': result['state'],
            'ssl':  'Disable' if result['ssl_enable'] is False else 'Enabled'
        }
        output_keys = {'name', 'state', 'datacenter', 'ssl', 'algorithm'}
        output_generic(gandi, output_base, output_keys, justify=14)

        gandi.echo('Vhosts :')
        for vhost in result['vhosts']:
            output_vhosts = ['vhost', 'ssl']
            vhost['vhost'] = vhost['name']
            vhost['ssl'] = 'Disable' if vhost['cert_id'] is None else 'Enabled'
            output_sub_generic(gandi, vhost, output_vhosts, justify=14)
        gandi.echo('Servers :')
        for server in result['servers']:
            ip = gandi.ip.info(server['ip'])
            iface = gandi.iface.info(ip['iface_id'])
            server['name'] = gandi.iaas.info(iface['vm_id'])['hostname']
            output_servers = ['name', 'ip', 'port', 'state']
            output_sub_generic(gandi, server, output_servers, justify=14)
        gandi.echo('Probe :')
        output_probe = ['state', 'host', 'interval', 'method', 'response',
                        'threshold', 'timeout', 'url', 'window']
        result['probe']['state'] = 'Disable' if result['probe']['enable'] is False else 'Enabled'
        output_sub_generic(gandi, result['probe'], output_probe, justify=14)
    elif format:
        output_json(gandi, format, result)
    return result


@cli.command()
@click.option('--datacenter', '-dc', type=DATACENTER,
              help="Datacenter where the webaccelerator will be created")
@click.option('--backend', '-b', type=BACKEND, multiple=True,
              help="Backend to add in the webaccelerator, use ip:port")
@click.option('--port', '-p', type=click.INT, required=False,
              help="set a default port backend if not specified with backend")
@click.option('--vhost', '-v', help="Vhost to add in the webaccelerator",
              multiple=True)
@click.option('--algorithm', type=click.Choice(['client-ip', 'round-robin']),
              help="Choose the loadbalancer algorithm", default='client-ip')
@click.option('--ssl-enable', is_flag=True,
              help="Activate SSL support on the webaccelerator")
@click.option('--zone-alter', is_flag=True,
              help="Alter the zone file of the domain for the vhost if domains"
              "are registred at Gandi")
@click.argument('name')
@pass_gandi
def create(gandi, name, datacenter, backend, port, vhost, algorithm,
           ssl_enable, zone_alter):
    """ Create a webaccelerator """
    backends = backend
    for backend in backends:
        # Check if a port is set for each backend, else set a default port
        if 'port' not in backend:
            if not port:
                backend['port'] = click.prompt('Please set a port for '
                                               'backends. If you want to set '
                                               'different port for each '
                                               'backend, use `-b ip:port`',
                                               type=int)
    result = gandi.webacc.create(name, datacenter, backends, vhost, algorithm,
                                 ssl_enable, zone_alter)
    return result


@cli.command()
@click.option('--vhost', '-v', help="Remove vhosts in the webaccelerator",
              multiple=True, type=WEBACC_VHOST_NAME)
@click.option('--backend', '-b', help="Remove backends in the webaccelerator",
              multiple=True)
@click.option('--webacc', '-w', type=WEBACC_NAME, required=False)
@pass_gandi
def delete(gandi, webacc, vhost, backend):
    """ Delete a webaccelerator, a vhost or a backend """
    if webacc:
        result = gandi.webacc.delete(resource)
    if backend:
        backends = backend
        for backend in backends:
            result = gandi.webacc.backend_remove(backend)
            return result
    if vhost:
        vhosts = vhost
        for vhost in vhosts:
            gandi.echo(vhost)
            result = gandi.webacc.vhost_remove(vhost)
            return result


@cli.command()
@click.option('--vhost', '-v', help="Add vhosts in the webaccelerator",
              multiple=True)
@click.option('--zone-alter', is_flag=True,
              help="Alter and active zone file if Gandi DNS are used for"
                   " the domain",)
@click.option('--backend', '-b', help="Add backends in the webaccelerator",
              type=BACKEND, multiple=True)
@click.option('--port', '-p', type=click.INT, required=False,
              help="set a default port backend if not specified with backend")
@click.argument('resource', type=WEBACC_NAME)
@pass_gandi
def add(gandi, resource, vhost, zone_alter, backend, port):
    """ Add a backend or a vhost on a webaccelerator """
    if backend:
        backends = backend
        for backend in backends:
            # Check if a port is set for each backend, else set a default port
            if 'port' not in backend:
                if not port:
                    backend['port'] = click.prompt('Please set a port for '
                                                   'backends. If you want to '
                                                   ' different port for '
                                                   'each backend, use `-b '
                                                   'ip:port`', type=int)
            result = gandi.webacc.backend_add(resource, backends)
    if vhost:
        vhosts = vhost
        for vhost in vhosts:
            params = {'vhost': vhost}
            if zone_alter:
                params['zone_alter'] = zone_alter
            result = gandi.webacc.vhost_add(resource, params)
    return result


@cli.command()
@click.option('--backend', '-b', help="Enable backends in the webaccelerator",
              multiple=True)
@click.option('--probe', '-p', help="Enable probe for the webaccelerator",
              is_flag=True)
@pass_gandi
def enable(gandi, backend):
    """ Enable a backend or a prove on a webaccelerator """
    result = gandi.webacc.backend_enable(resource, backend)
    return result


@cli.command()
@click.option('--backend', '-b', help="Disable backends in the webaccelerator",
              multiple=True)
@click.option('--probe', '-p', help="Disable probe for the webaccelerator",
              is_flag=True)
@pass_gandi
def disable(gandi, backend):
    """ Disable a backend or a probe on a webaccelerator """
    result = gandi.webacc.backend_disable(resource, backend)
    return result


@cli.command()
@click.option('--enable', '-e', is_flag=True,
              help="Enable the probe on the webaccelerator")
@click.option('--disable', '-d', is_flag=True,
              help="Disable the probe on the webaccelerator")
@click.option('--test', is_flag=True, help="Test probe on the webaccelerator")
@click.option('--host', '-h', help="Set the host to test")
@click.option('--interval', '-i', help="Set interval for the probe",
              type=click.INT)
@click.option('--http-method', '-m', help="Choose HTTP method for the probe",
              type=click.Choice(['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']))
@click.option('--http-response', '-r', type=click.INT,
              help="HTTP respond code expected by the probe")
@click.option('--threshold', '-t', type=click.INT,
              help="Number of probes to consider in the window")
@click.option('--timeout', help="Timeout in seconds",
              type=click.INT)
@click.option('--url', '-u', help="Probe url in the virtual host",
              type=click.STRING)
@click.option('--window', '-w', type=click.INT,
              help="Total number of probes to consider health decision")
@click.argument('resource', type=WEBACC_NAME)
@pass_gandi
def probe(gandi, resource, enable, disable, test, host, interval, http_method,
          http_response, threshold, timeout, url, window):
    """ Manage a probe for a webaccelerator """
    result = gandi.webacc.probe(resource, enable, disable, test, host,
                                interval, http_method, http_response,
                                threshold, timeout, url, window)
    output_keys = ['status', 'timeout']
    output_generic(gandi, result, output_keys, justify=14)
    return result
