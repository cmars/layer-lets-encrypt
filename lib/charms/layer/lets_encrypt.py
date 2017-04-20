from charmhelpers.core import hookenv


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
