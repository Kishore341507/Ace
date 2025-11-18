# Security Policy

## Supported Versions

This project is currently in active development. Security updates are provided for the latest version only.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| Older   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability within this project, please follow these steps:

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Send an email to the repository owner or use GitHub's private security advisory feature
3. Include as much information as possible:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if you have one)

### What to Expect

- **Response Time**: We aim to acknowledge receipt of your vulnerability report within 48 hours
- **Updates**: We will keep you informed about the progress of fixing the vulnerability
- **Credit**: We will credit you for responsibly disclosing the issue (unless you prefer to remain anonymous)

### Security Best Practices for Users

When deploying this bot:

1. **Never commit your `.env` file** - It contains sensitive credentials
2. **Use strong, unique passwords** for your PostgreSQL database
3. **Keep your Discord bot token secure** - Never share it publicly
4. **Regularly update dependencies** - Run `pip install -r requirements.txt --upgrade` periodically
5. **Review permissions** - Only grant necessary Discord permissions to the bot
6. **Use GitHub Secrets** - Store sensitive deployment information in GitHub Secrets, not in code
7. **Enable 2FA** - Use two-factor authentication on your GitHub account

## Configuration Security

Ensure the following environment variables are properly configured and never committed to the repository:

- `TOKEN` - Your Discord bot token
- `DB` - Your PostgreSQL database connection string
- `ERROR_CHANNEL_ID` - (Optional) Channel ID for error logging
- `BUG_REPORT_CHANNEL_ID` - (Optional) Channel ID for bug reports

For deployment, also configure these GitHub Secrets:

- `GCP_SSH_PRIVATE_KEY` - SSH private key for deployment
- `GCP_VM_IP` - IP address of your deployment server
- `GCP_USERNAME` - Username for SSH connection

## Known Security Considerations

- This bot requires elevated Discord permissions (see README.md)
- Database credentials must be properly secured
- Custom emoji IDs are specific to your Discord server
- Ensure proper rate limiting is configured to prevent abuse

## Disclaimer

This software is provided "as is" without warranty of any kind. Users are responsible for securing their own deployments and configurations.
