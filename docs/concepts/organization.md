# Organization

**Organization** is the top-level object in the Launchable object model.

## Users and workspaces

**Users** are members of organizations. **Workspaces** belong to organizations.

A user may be a member of only one organization at a time. All members of an organization can access all workspaces in that organization.

If your organization has multiple workspaces, you can navigate between them using the dropdown in the left navigation.

If you'd like to create a new workspace in your organization, contact your customer success manager.

## Organization settings

Organization settings can be found on the settings page in any _workspace_ in your organization:

![](../.gitbook/assets/launchable\_settings\_20220613.png)

### Organization invitation link

Create an invitation link to invite your teammates to access the Launchable dashboard. Just create a single link and share it with your team. After they click the link and sign up for an account, they'll be prompted to join your organization.

![](../.gitbook/assets/launchable\_invite\_url\_20220613.png)

Invitation links expire after 30 days. After that, simply create a new one.

### SAML 2.0

Launchable supports SAML 2.0 for SSO authentication. Most Identity Providers (e.g. Okta, OneLogin, etc.) support SAML 2.0 for SSO.

Contact your customer success manager to enable this feature for your organization. In the process, you'll need to provide Launchable an X.509 signing certificate from your Identity Provider in PEM or CER format.

After SAML is enabled for your organization, all organization members must log in with SAML using an account under your email domain. They can't log in with their previous credentials such as an email and password combination or a GitHub account.

