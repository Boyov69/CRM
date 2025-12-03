# Contributing to Huisartsen CRM

First off, thank you for considering contributing to this project! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why this would be useful
- **Proposed solution** or implementation ideas
- **Alternatives considered**

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Write or update tests if applicable
5. Update documentation
6. Commit your changes (see [Commit Messages](#commit-messages))
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/CRM.git
cd CRM

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set SECRET_KEY and one email provider
```

### Running Locally

```bash
# Start the application
python app.py

# The app will be available at http://localhost:5000
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) style guidelines:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions and classes
- Use type hints where possible

### Code Organization

- Keep functions small and focused (single responsibility)
- Group related functionality in modules
- Avoid circular dependencies
- Use meaningful file and module names

### Example

```python
def send_email_campaign(practice_ids: list[int], template: str, use_ai: bool = False) -> dict:
    """
    Send email campaign to specified practices.
    
    Args:
        practice_ids: List of practice IDs to target
        template: Email template identifier
        use_ai: Whether to use AI for personalization
        
    Returns:
        Dictionary with campaign results (sent, failed, details)
        
    Raises:
        ValueError: If template doesn't exist
    """
    # Implementation
    pass
```

### Testing

```bash
# Run tests (when available)
pytest

# Run with coverage
pytest --cov=modules --cov-report=html

# Linting
flake8 .

# Type checking
mypy app.py modules/
```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear commit history:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies
- **perf**: Performance improvements

### Examples

```bash
# Simple feature
git commit -m "feat: add email template preview"

# Bug fix with details
git commit -m "fix: resolve Gmail API token refresh issue

The token was not being refreshed properly when expired,
causing authentication failures. Now implements proper
refresh logic with error handling."

# Breaking change
git commit -m "feat!: change API response format

BREAKING CHANGE: API responses now use camelCase instead of
snake_case for consistency with frontend."
```

### Scope Examples

- `email`: Email-related changes
- `api`: API endpoint changes
- `ui`: User interface changes
- `db`: Database changes
- `scraper`: Web scraping functionality
- `analytics`: Analytics/reporting features

## Pull Request Process

### Before Submitting

1. **Update documentation** if you've changed functionality
2. **Add tests** for new features when possible
3. **Run linters** to ensure code quality
4. **Test locally** to verify changes work
5. **Update CHANGELOG.md** with your changes

### PR Title

Use conventional commit format:

```
feat: add email scheduling feature
fix: resolve database connection timeout
docs: improve installation instructions
```

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
Describe how you tested these changes.

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests (if applicable)
```

### Review Process

1. At least one maintainer review required
2. All CI checks must pass
3. Address review feedback
4. Maintainer will merge when approved

## Questions?

Feel free to open an issue or reach out to the maintainers:

- GitHub Issues: https://github.com/Boyov69/CRM/issues
- Email: artur@zorgcore.be

Thank you for contributing! 🙏
