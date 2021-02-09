# Troubleshooting

## Verification failure

### Connectivity

If you receive an error like this one, then you'll need to configure your firewall to allow traffic to `api-static.mercury.launchableinc.com`:

```bash
$ launchable verify
unable to post to https://api.mercury.launchableinc.com/...
```

If you need to interact with the API via static IPs, first set the `LAUNCHABLE_BASE_URL` environment variable to `https://api-static.mercury.launchableinc.com`.

The IP for this hostname will be either `13.248.185.38` or `76.223.54.162` which you can add to your firewall settings.

