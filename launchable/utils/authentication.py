import os
from typing import Tuple

import click
import requests

from .env_keys import ORGANIZATION_KEY, TOKEN_KEY, WORKSPACE_KEY


def get_org_workspace():
    token = os.getenv(TOKEN_KEY)
    if token:
        try:
            _, user, _ = token.split(":", 2)
            org, workspace = user.split("/", 1)
            return org, workspace
        except ValueError:
            return None, None

    return os.getenv(ORGANIZATION_KEY), os.getenv(WORKSPACE_KEY)


def ensure_org_workspace() -> Tuple[str, str]:
    org, workspace = get_org_workspace()
    if org is None or workspace is None:
        raise click.UsageError(
            click.style(
                "Could not identify Launchable organization/workspace. "
                "Please confirm if you set LAUNCHABLE_TOKEN or LAUNCHABLE_ORGANIZATION and "
                "LAUNCHABLE_WORKSPACE environment variables",
                fg="red"))
    return org, workspace


def authentication_headers():
    token = os.getenv(TOKEN_KEY)
    if token:
        return {'Authorization': 'Bearer {}'.format(token)}

    if os.getenv('EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH'):
        req_url = os.getenv('ACTIONS_ID_TOKEN_REQUEST_URL')
        rt_token = os.getenv('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
        if not req_url or not rt_token:
            raise click.UsageError(
                click.style(
                    "GitHub Actions OIDC tokens cannot be retrieved."
                    "Confirm that you have added necessary permissions following "
                    "https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-cloud-providers#adding-permissions-settings",  # noqa: E501
                    fg="red"))
        r = requests.get(req_url,
                         headers={
                             'Authorization': 'Bearer {}'.format(rt_token),
                             'Accept': 'application/json; api-version=2.0',
                             'Content-Type': 'application/json',
                         })
        r.raise_for_status()
        return {'Authorization': 'Bearer {}'.format(r.json()['value'])}

    if os.getenv('GITHUB_ACTIONS'):
        headers = {
            'GitHub-Actions': os.environ['GITHUB_ACTIONS'],
            'GitHub-Run-Id': os.environ['GITHUB_RUN_ID'],
            'GitHub-Repository': os.environ['GITHUB_REPOSITORY'],
            'GitHub-Workflow': os.environ['GITHUB_WORKFLOW'],
            'GitHub-Run-Number': os.environ['GITHUB_RUN_NUMBER'],
            'GitHub-Event-Name': os.environ['GITHUB_EVENT_NAME'],
            'GitHub-Sha': os.environ['GITHUB_SHA'],
        }

        # GITHUB_PR_HEAD_SHA might not exist
        pr_head_sha = os.getenv('GITHUB_PR_HEAD_SHA')
        if pr_head_sha:
            headers['GitHub-Pr-Head-Sha'] = pr_head_sha

        return headers
    return {}
