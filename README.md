# layer-lets-encrypt

# Operating a Charm that uses this layer

Charms using this layer will automatically request and renew a Let's Encrypt certificate for the `fqdn` specified in the Charm config.

## Requirements

Let's Encrypt registration will only work in deployments that meet the
following criteria:

- Placement onto a machine with a public IPv4 address. IPv6 might work (Let's
  Encrypt supports it), but this is unconfirmed.
  - Container placement will not work. Containers aren't typically publicly
    route-able.
  - Private networks will not work. For private TLS, I recommend using
    layer:tls-client with easyrsa.
- Registered DNS "A" record for the above public address.
  - Must be a domain name allowed by Let's Encrypt. Some, such as
    *.amazonaws.com dynamic addresses, are not allowed.
- Must be exposed (`juju expose`) so that Let's Encrypt can reach it for
  registration.

## Configuration

This layer adds a config option `fqdn` to `config.yaml`. When set, this layer
will attempt to register the hostname with Let's Encrypt. Only set `fqdn`:
- _After_ the DNS "A" record has been established for the unit's public IP
  address.
- The registered domain name has had time to propagate.
- The application has been `juju expose`d.

A `contact-email` config option may also be set, for receiving email from Let's Encrypt regarding certification of the domain name. *Note that changing `contact-email` after the certificate has been requested will not have any effect.*

# Developing a Charm with this layer

Include `layer:lets-encrypt` in your web application charm and set the `fqdn` config option to automatically obtain a TLS certificate from Let's Encrypt.

Once the application is registered with Let's Encrypt, the reactive state
`lets-encrypt.registered` will be set. Then, in your charm, you may obtain the
path to the certificates and keys with `charms.layer.lets_encrypt.live()`.

## Example: Using with layer:nginx

Configure layer:lets-encrypt to restart nginx during registration:

```yaml
options:
  lets-encrypt:
    service-name: nginx
```

Use the obtained certificates in your charm layer. For example:

```python
from charmhelpers.core import hookenv
from charms.layer import lets_encrypt

...

@when('nginx.available', 'lets-encrypt.registered')
@when_not('myapp.web.configured')
def configure_webserver():
    status_set('maintenance', 'Configuring website')
	fqdn = config().get('fqdn')
    live = lets_encrypt.live()
    configure_site('myapp', 'myapp.nginx.tmpl',
                   key_path=live['privkey'],
                   crt_path=live['fullchain'], fqdn=fqdn)
    host.service_restart('nginx')
    status_set('active', 'Website available: https://%s' % fqdn)
```

You'll want to use the `fqdn` for `server_name` in your nginx site config.

Let's Encrypt registration may be disabled by setting the
`lets-encrypt.disable` state. If you know your charm isn't ready to register,
or doesn't need it -- maybe it's being TLS terminated by a front end -- please
set this to avoid wasting Let's Encrypt resources.

Certificate renewal may be disabled by setting the `lets-encrypt.renew.disable`
state. Set this to prevent the `lets-encrypt` layer from temporarily stopping
the configured `service-name` during certificate renewal.

# Caveats

The configured `service-name` will be temporarily stopped while Let's Encrypt
registers and renews with the "standalone" method.

This layer is only supported on xenial. If deployed on earlier series, this
layer does nothing.

This layer requires agreement to the ISRG Let's Encrypt terms of service in
order to deploy, because registration is done non-interactively in the charm.

# TODOs

Some things could be improved:

- Better rate-limiting of the registration retries.
- Not attempting to register if not exposed (can this be detected?).
- Not attempting to register if FQDN isn't ready, or is incorrect.
- Non-interrupting methods like webroot.

# License

See LICENSE.layer-lets-encrypt for details.
