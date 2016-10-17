from subprocess import check_call

from charms.reactive import (
    when,
    when_not,
    set_state,
    remove_state,
    hook
)

from charmhelpers.core.host import (
    lsb_release,
    service_running,
    service_start,
    service_stop
)

from charmhelpers.core.hookenv import (
    log,
    config,
    open_port,
    status_set
)

import charms.apt


@when_not('apt.installed.lets-encrypt')
def check_version_and_install():
    series = lsb_release()['DISTRIB_CODENAME']
    if not series >= 'xenial':
        log('letsencrypt not supported on series >= %s' % (series))
        status_set('blocked', "Unsupported series < Xenial")
        return
    else:
        charms.apt.queue_install(['lets-encrypt'])
        charms.apt.install_queued()


@hook('config-changed')
def config_changed():
    configs = config()
    if configs.changed('fqdn') and configs.previous('fqdn') \
       or configs.get('fqdn'):
        remove_state('lets-encrypt.registered')


@when('apt.installed.lets-encrypt')
@when_not('lets-encrypt.registered')
@when_not('lets-encrypt.disable')
def register_server():
    configs = config()
    fqdn = configs.get('fqdn')
    if not fqdn:
        set_state('lets-encrypt.configured')
        return

    needs_start = False
    if service_running('nginx'):
        needs_start = True
        service_stop('nginx')

    open_port(80)
    open_port(443)

    mail_args = []
    if config.get('contact-email'):
        mail_args.append('--email')
        mail_args.append(config.get('contact-email'))
    else:
        mail_args.append('--register-unsafely-without-email')
    try:
        # Agreement already captured by terms, see metadata
        le_cmd = ['letsencrypt', 'certonly', '--standalone', '--agree-tos',
                  '--non-interactive', '-d', fqdn]
        le_cmd.extend(mail_args)
        check_call(le_cmd)
        status_set('active', 'registered %s' % (fqdn))
        set_state('lets-encrypt.registered')
    except:
        status_set('blocked', 'letsencrypt registration failed')
    finally:
        if needs_start:
            service_start('nginx')
