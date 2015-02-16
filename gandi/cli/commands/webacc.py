""" Webaccelerator namespace commands. """

import click

from gandi.cli.core.cli import cli
from gandi.cli.core.utils import (
  output_generic, output_list
)
from gandi.cli.core.params import (
  pass_gandi, IPPORT, DATACENTER
)

import json

@cli.command()
@click.option('--limit', help="Limit the number of results", default=100,
              show_default=True)
@click.option('--format', type=click.Choice(['json']), required=False,
              help="Choose the output format")
@pass_gandi
def list(gandi, limit, format):
    """List webaccelerator"""
    options = {
        'items_per_page': limit,
    }

    result = gandi.webacc.list(options)

    output_keys = ['name', 'state', 'ssl']

    for webacc in result:
            webacc['ssl'] = 'Disable' if webacc['ssl_enable'] == False else 'Enabled'
            output_generic(gandi, webacc, output_keys, justify=14)
            gandi.separator_line('-', 4)
            for vhost in webacc['vhosts']:
                  output_vhosts = ['vhost', 'ssl']
                  vhost['vhost'] = vhost['name']
                  vhost['ssl'] = 'Disable' if vhost['cert_id'] == None else 'Enabled'
                  output_generic(gandi, vhost, output_vhosts, justify=14)

            gandi.separator_line('-', 4)

            for server in webacc['servers']:
                ip = gandi.ip.info(server['ip'])
                iface = gandi.iface.info(ip['iface_id'])
                server['name'] = gandi.iaas.info(iface['vm_id'])['hostname']
                output_servers = ['name', 'ip', 'port', 'state']
                output_generic(gandi, server, output_servers, justify=14)
                gandi.separator_line('-', 2)
    return result

@cli.command()
@click.argument('resource')
@pass_gandi
def info(gandi, resource):
    """ Dislay information about a rproxy """
    result = gandi.webacc.info(name)
    output_base = {
        'name': result['name'],
        'algorithm': result['lb']['algorithm'],
        'datacenter' : result['datacenter']['name'],
        'state' : result['state'],
        'ssl' :  'Disable' if result['ssl_enable'] == False else 'Enabled'
    } 
    output_keys = {'name', 'state', 'datacenter', 'ssl', 'algorithm'}
    output_generic(gandi, output_base, output_keys, justify=14)
    
    gandi.separator_line('-', 4)
    for vhost in result['vhosts']:
        output_vhosts = ['vhost', 'ssl']
        vhost['vhost'] = vhost['name']
        vhost['ssl'] = 'Disable' if vhost['cert_id'] == None else 'Enabled'
        output_generic(gandi, vhost, output_vhosts, justify=14)

    gandi.separator_line('-', 4)

    for server in result['servers']:
        ip = gandi.ip.info(server['ip'])
        iface = gandi.iface.info(ip['iface_id'])
        server['name'] = gandi.iaas.info(iface['vm_id'])['hostname']
        output_servers = ['name', 'ip', 'port', 'state']
        output_generic(gandi, server, output_servers, justify=14)
        gandi.separator_line('-', 2)

    gandi.separator_line('-', 4)

    output_probe = ['state', 'host', 'interval', 'method', 'response', 'threshold', 'timeout', 'url', 'window']
    result['probe']['state'] = 'Disable' if result['probe']['enable'] == False else 'Enabled'
    output_generic(gandi, result['probe'], output_probe, justify=14)
    
    return result

@cli.command()
@click.option('--datacenter', '-dc', type=DATACENTER, 
              help="Datacenter where the webaccelerator will be created")
@click.option('--server', '-s', type=IPPORT, multiple=True, 
              help="Server to add into the webaccelerator")
@click.argument('name')
@pass_gandi
def create(gandi, name, datacenter, server, vhosts, algorithm, ssl_enable, zone_alter):
    """ Create a rproxy """