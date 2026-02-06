# Contributing to Pi Command Center

First off, thank you for considering contributing to Pi Command Center! It's people like you that make this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming environment. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (Pi model, OS version, Python version)
- **Logs** if applicable (`sudo journalctl -u pibot -n 50`)

### 💡 Suggesting Features

Feature suggestions are welcome! Please include:

- **Use case**: Why would this be useful?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other ways to solve the problem

### 🔧 Pull Requests

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and create a Pull Request

## Development Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- A Raspberry Pi (or Linux machine for development)

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pi-command-center.git
cd pi-command-center

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create test environment file
cp .env.example .env.test
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_network.py
```

### Code Style

```bash
# Format code
black .

# Check linting
flake8

# Type checking
mypy .
```

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features
3. **Follow the style guide** (see below)
4. **Update CHANGELOG.md** if applicable
5. **Request review** from maintainers

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, no code change
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(vpn): add support for multiple VPN endpoints
fix(bot): handle timeout errors in status command
docs(readme): add troubleshooting section
```

## Style Guidelines

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names

```python
# Good
async def get_device_status(device_mac: str) -> DeviceStatus:
    """Get the current status of a device by MAC address."""
    ...

# Bad
async def get(m):
    ...
```

### Documentation

- Use clear, concise language
- Include code examples
- Keep README updated
- Document all public APIs

### Testing

- Write tests for new features
- Maintain >80% coverage
- Test edge cases
- Use meaningful test names

```python
def test_vpn_split_mode_routes_matching_domains_through_tunnel():
    ...
```

## Project Structure

```
pi-command-center/
├── handlers/          # Telegram bot handlers
├── services/          # Business logic
├── keyboards/         # Bot keyboards
├── utils/             # Utilities
├── tests/             # Test files
├── docs/              # Documentation
├── scripts/           # Installation scripts
├── docker/            # Docker configuration
└── configs/           # Configuration templates
```

## Questions?

Feel free to open an issue for any questions or discussions!
