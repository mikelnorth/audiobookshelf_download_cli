# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version  | Supported          |
| -------- | ------------------ |
| Latest   | :white_check_mark: |
| < Latest | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, please follow these steps:

1. **Do Not** disclose the vulnerability publicly
2. Email the details to the project maintainers (create a private security advisory on GitHub)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (if you have them)

## What to Expect

- Acknowledgment of your report within 48 hours
- Regular updates on the progress
- Credit for your discovery (if you wish)

## Security Best Practices

When using this tool:

### API Key Storage

- API keys are encrypted using PBKDF2 (100,000 iterations) with SHA256
- Master passwords are stored in your OS keychain (macOS Keychain, Windows Credential Manager, etc.)
- Hybrid encryption combines master password + hardware ID
- Never share your API keys or master password

### File Permissions

- Configuration files are automatically set to restrictive permissions (0o600)
- Keep your downloads directory secure
- Don't share your `.audiobookshelf_keys` file

### Network Security

- Always use HTTPS for server connections
- Verify your server's SSL certificate
- Use a secure network when downloading

### General Security

- Keep Python and dependencies up to date
- Regularly review stored API keys and remove unused ones
- Use unique API keys for each installation
- Set API key expiration dates in Audiobookshelf when possible

## Known Security Considerations

### Encryption Limitations

- Encryption protects against casual access to stored keys
- Physical access to your machine by an attacker may compromise keys
- The security relies on your OS keychain implementation
- On systems without hardware ID, a user-generated system key is required

### Download Security

- Downloaded files are saved in plain text
- Ensure your downloads directory has appropriate access controls
- Be cautious when downloading to shared directories

## Updates

We will update this policy as needed. Check back regularly for changes.

## Questions

If you have questions about security that aren't vulnerabilities:

- Open a GitHub issue with the "security" label
- Check documentation first (README.md, docs/API_KEYS.md)
