# Contributing to Speed Reader

Thank you for your interest in contributing to Speed Reader! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the issue has already been reported in the [Issues](https://github.com/yourusername/speed-reader/issues) section
2. If not, create a new issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Screenshots if applicable

### Suggesting Features

1. Check existing issues for similar suggestions
2. Create a new issue with the "enhancement" label
3. Describe the feature clearly
4. Explain why it would be valuable
5. Consider implementation complexity

### Contributing Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Write or update tests
5. Ensure code follows the style guidelines
6. Test your changes thoroughly
7. Submit a pull request

## Development Setup

See the [README.md](README.md) for detailed setup instructions.

## Code Style

### Python Style

- Follow [PEP 8](https://pep8.org/) guidelines
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. Install them with:

```bash
pip install pre-commit
pre-commit install
```

The hooks will run automatically on `git commit` and check:
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Basic file checks

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add more detail in the body if needed

Example:
```
Add speed history feature

- Save user's preferred reading speed between sessions
- Add speed presets dropdown for quick selection
- Update UI to show current speed in presets
```

### Pull Request Guidelines

- Reference any related issues
- Provide a clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Ensure CI checks pass (GitHub Actions)
- Update documentation if needed

## Testing

- Write unit tests for new functionality
- Test on multiple platforms if possible (Windows, Linux, macOS)
- Test with different file formats
- Verify edge cases and error conditions

## Documentation

- Update README.md for significant changes
- Add docstrings to new functions
- Update type hints
- Document any new configuration options

## Architecture Guidelines

### File Organization

- Keep related functionality together
- Use clear, descriptive module names
- Avoid deep nesting of directories

### GUI Code

- Separate UI logic from business logic
- Use Qt signals/slots appropriately
- Follow the existing styling patterns
- Ensure responsive design

### Parser Code

- Handle errors gracefully
- Provide meaningful error messages
- Support as many file formats as possible
- Optimize for performance with large files

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create a git tag
4. Build and test executables
5. Create GitHub release

## Getting Help

- Check existing documentation first
- Search existing issues
- Ask questions in new issues
- Be patient and respectful

Thank you for contributing to Speed Reader!