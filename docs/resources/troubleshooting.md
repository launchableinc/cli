# Troubleshooting

## Verification failure

### Firewalls and static IP addresses

If you receive an error like this one, then you'll need to configure your firewall to allow traffic to `api-static.mercury.launchableinc.com`:

```bash
$ launchable verify
unable to post to https://api.mercury.launchableinc.com/...
```

If you need to interact with the API via static IPs, first set the `LAUNCHABLE_BASE_URL` environment variable to `https://api-static.mercury.launchableinc.com`.

The IP for this hostname will be either `13.248.185.38` or `76.223.54.162` which you can add to your firewall settings.

### Proxies and certificates

If your CI server sits behind a proxy, you can tell the CLI to use it by setting the `HTTP_PROXY` and/or `HTTPS_PROXY` environment variables. For example:

```bash
export HTTP_PROXY="http://10.10.1.10:3128"
export HTTPS_PROXY="http://10.10.1.10:1080"
```

Similarly, if you need to specify a certificate:

```bash
export curl_ca_bundle="/usr/local/myproxy_info/cacert.pem"
```

These examples come from the [documentation for Requests](https://requests.readthedocs.io/en/master/user/advanced/#proxies), which the CLI uses under the hood. See that page for more details.

