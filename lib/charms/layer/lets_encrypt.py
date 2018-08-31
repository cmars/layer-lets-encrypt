import os
from charmhelpers.core import (
    hookenv,
    unitdata
)
from charms.reactive import remove_state, set_state
from charms.reactive.helpers import data_changed


def live():
    """live returns a dict containing the paths of certificate and key files
    for the configured FQDN."""

    fqdn = hookenv.config().get('fqdn')
    if not fqdn:
        return None
    return {
        'fullchain': '/etc/letsencrypt/live/%s/fullchain.pem' % (fqdn),
        'chain': '/etc/letsencrypt/live/%s/chain.pem' % (fqdn),
        'cert': '/etc/letsencrypt/live/%s/cert.pem' % (fqdn),
        'privkey': '/etc/letsencrypt/live/%s/privkey.pem' % (fqdn),
        'dhparam': '/etc/letsencrypt/dhparam.pem',
    }


def live_all():
    """live_all returns a dict containing per fqdn the paths of certificate and
    key files.

    Multiple domain certificates will only return one dict using one of the fqdn as key."""
    requests = unitdata.kv().get('certificate.requests', [])
    if not requests:
        return None
    certificates = {}
    for request in requests:
        for fqdn in request['fqdn']:
            if os.path.exists('/etc/letsencrypt/live/%s/fullchain.pem' % (fqdn)):
                certificates[fqdn] = {
                    'fullchain': '/etc/letsencrypt/live/%s/fullchain.pem' % (fqdn),
                    'chain': '/etc/letsencrypt/live/%s/chain.pem' % (fqdn),
                    'cert': '/etc/letsencrypt/live/%s/cert.pem' % (fqdn),
                    'privkey': '/etc/letsencrypt/live/%s/privkey.pem' % (fqdn),
                    'dhparam': '/etc/letsencrypt/dhparam.pem',
                }
    return certificates


def set_requested_certificates(requests):
    """takes a list of requests which has the following format:
        [{
            'fqdn': ['example.com', 'blog.example.com'],
            'contact-email': 'example@example.com'
        }]
        each list item will request one certificate.
    """
    if not data_changed('cert.requests', requests) and not requests:
        return
    unitdata.kv().set('certificate.requests', requests)
    remove_state('lets-encrypt.registered')
    remove_state('lets-encrypt.certificate-requested') # reset so handler will rerun even if it already ran
    set_state('lets-encrypt.certificate-requested')
