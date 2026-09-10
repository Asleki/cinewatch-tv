# CineWatch TV Security Policy

CineWatch TV V1 is private and invite-only.

## Reporting

Do not place suspected credentials, tokens, passwords, private keys, database
connection strings, personal data, or exploit payloads in a public issue.

For the current private-development phase, report security concerns directly
to the repository owner/development team through an existing private channel.

## Repository security rules

The repository must not contain:

- database passwords;
- GitHub personal access tokens;
- raw AWS access keys, secret keys, or session tokens;
- private keys or certificate private material;
- provider API secrets in browser-visible variables;
- NPP credentials or NPP database connection material.

Runtime secrets are supplied only through approved local or cloud secret
mechanisms when the corresponding infrastructure exists.

## CI trust boundary

Pull-request CI is read-only. CI does not receive CineWatch database,
provider, GitHub PAT, AWS, Azure, or other application secrets.

Cloud deployment and production incident-response policy are outside
CWTV.V1.2.8 and will be governed by later milestones.
