import os

def parse_token():
  try:
    token = os.environ["LAUNCHABLE_TOKEN"]
    _, user, _ = token.split(":", 2)
    org, workspace = user.split("/", 1)
  except:
    exit("Please specify valid LAUNCHABLE_TOKEN")
  return token, org, workspace
