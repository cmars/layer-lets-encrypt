# layer-lets-encrypt

# Usage

Include `layer:lets-encrypt` in your `layer.yaml` where you'd use
`layer:nginx`. `layer:lets-encrypt` includes `layer:nginx`.

This layer adds a config option `fqdn` to your `config.yaml`. When set, this
layer will attempt to register the hostname with Let's Encrypt.

When registered, the reactive state `lets-encrypt.registered` will be set.
Then, in your charm, you may obtain the path to the certificates and keys with
`charms.layer.letsencrypt.live()`, and configure nginx accordingly:

```python
from charmhelpers.core import hookenv
from charms.layer import letsencrypt

...

@when('nginx.available', 'lets-encrypt.registered')
@when_not('myapp.web.configured')
def configure_webserver():
    status_set('maintenance', 'Configuring website')
	fqdn = config().get('fqdn')
    live = letsencrypt.live()
    configure_site('myapp', 'myapp.nginx.tmpl',
                   key_path=live['privkey'],
                   crt_path=live['fullchain'], fqdn=fqdn)
    host.service_restart('nginx')
    status_set('active', 'Website available: https://%s' % fqdn)
```

Let's Encrypt registration may be disabled by setting the
`lets-encrypt.disable` state. If you know your charm isn't ready to register,
or doesn't need it -- maybe it's being TLS terminated by a front end -- please
set this to avoid wasting Let's Encrypt resources.

# Caveats

nginx will be temporarily stopped while Let's Encrypt registers with the
"standalone" method.

This layer is only supported on xenial. If deployed on earlier series, this
layer does nothing.

This layer requires agreement to the ISRG Let's Encrypt terms of service in
order to deploy, because registration is done non-interactively in the charm.

# TODOs

Some things could be improved:

- Support for automatic renewals, or even manual renewals with an action.
- Better rate-limiting the registration retries.
- Not attempting to register if not exposed (can this be detected?).

Some things are probably out of scope. This layer is intended for securing
standalone web applications:

- Registration behind an HTTP reverse proxy; alternative ports.
- Other methods like webroot.
- General purpose registration for charms that provide `interface:http` but
  don't use `layer:nginx`.

However, this layer might be a good starting point to develop such things.

# License

See LICENSE.layer-lets-encrypt for details.

