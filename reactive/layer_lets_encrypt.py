import glob
import os
import shutil

from subprocess import check_call, check_output

from charms.reactive import when, when_not, set_state, remove_state, hook

from charmhelpers.core import hookenv, host
from charmhelpers.fetch import apt_install


@hook('install')
def install():
    series = check_output(['lsb_release', '-c', '-s'], universal_newlines=True).strip()
    if series < 'xenial':
        hookenv.log('letsencrypt not supported on series %s' % (series))
        return
    set_state('lets-encrypt.installed')


@hook('config-changed')
def config_changed():
    config = hookenv.config()
    if config.changed('fqdn') and config.previous('fqdn') or config.get('fqdn'):
        remove_state('lets-encrypt.registered')


@when('lets-encrypt.installed')
@when_not('lets-encrypt.registered')
@when_not('lets-encrypt.disable')
def register_server():
    config = hookenv.config()
    fqdn = config.get('fqdn')
    if not fqdn:
        set_state('lets-encrypt.configured')
        return

    needs_start = False
    if host.service_running('nginx'):
        needs_start = True
        host.service_stop('nginx')

    hookenv.open_port(80)
    hookenv.open_port(443)

    mail_args = []
    if config.get('contact-email'):
        mail_args.append('--email')
        mail_args.append(config.get('contact-email'))
    else:
        mail_args.append('--register-unsafely-without-email')
    try:
        check_call(['letsencrypt', 'certonly', '--standalone',
            '--agree-tos',  # Agreement already captured by terms, see metadata
            '--non-interactive',
            '-d', fqdn, *mail_args])
        hookenv.status_set('active', 'registered %s' % (fqdn))
        set_state('lets-encrypt.registered')
    except:
        hookenv.status_set('blocked', 'letsencrypt registration failed')
    finally:
        if needs_start:
            host.service_start('nginx')
