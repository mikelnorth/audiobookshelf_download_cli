# Contributing to Audiobookshelf Downloader

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/audiobookshelf-downloader.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Security

- **Never commit API keys, passwords, or personal information**
- Use the provided encryption system for sensitive data
- Test security-related changes thoroughly
- Report security vulnerabilities privately (see SECURITY.md if it exists)

### Testing

- Test your changes locally before submitting
- Ensure all existing functionality still works
- Add tests for new features when applicable
- Test with different Python versions if possible (3.7+)

### Documentation

- Update README.md if you add new features
- Update relevant documentation files in `docs/` (API_KEYS.md, CONFIGURATION.md, etc.)
- Add comments for complex logic
- Keep documentation clear and concise

## Submitting Changes

1. Commit your changes with clear, descriptive messages:

   ```bash
   git commit -m "Add feature: brief description"
   ```

2. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

3. Open a Pull Request with:
   - Clear title and description
   - Reference to any related issues
   - Summary of changes made
   - Any breaking changes noted

## Pull Request Process

1. Ensure your PR description clearly describes the problem and solution
2. Update documentation as needed
3. The PR will be reviewed by maintainers
4. Address any feedback or requested changes
5. Once approved, your PR will be merged

## Code of Conduct

- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Questions?

If you have questions about contributing:

- Open an issue with the "question" label
- Check existing issues and documentation first
- Be specific about what you need help with

## Recognition

Contributors will be recognized in the project. Thank you for helping improve Audiobookshelf Downloader!
