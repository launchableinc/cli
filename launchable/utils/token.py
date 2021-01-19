import os


def parse_token():
    try:
        token = os.environ["LAUNCHABLE_TOKEN"]
        _, user, _ = token.split(":", 2)
        org, workspace = user.split("/", 1)
    except ValueError:
        exit("Please set LAUNCHABLE_TOKEN environment variable to the Launchable API token")
    return token, org, workspace
