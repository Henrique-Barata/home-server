# Contributing to Expenses Tracker

Thank you for your interest in contributing! This is a personal expense tracking app made public for others to use.

## How to Contribute

### Reporting Issues
- Check if the issue already exists
- Provide clear steps to reproduce
- Include your Python version and OS

### Suggesting Features
- Open an issue describing the feature
- Explain the use case and benefits
- Consider if it fits the "lightweight and simple" philosophy

### Code Contributions

1. **Fork the repository**

2. **Set up your development environment:**
   ```bash
   git clone <your-fork>
   cd expensesApp
   cp config_private.py.template config_private.py
   # Edit config_private.py with test values
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python init_db.py
   ```

3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes:**
   - Follow existing code style
   - Keep it simple and lightweight
   - Test your changes thoroughly
   - Don't commit personal data or config files

5. **Submit a pull request:**
   - Describe what you changed and why
   - Reference any related issues

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions small and focused

### Database Changes
- Create migration scripts for schema changes
- Test with existing data
- Document the migration process

### Performance
- This app is designed for low-resource systems
- Avoid heavy dependencies
- Keep queries efficient
- Test on modest hardware

### Security
- Never commit passwords or personal data
- Review security implications of changes
- Keep dependencies updated

## Project Philosophy

This app prioritizes:
- **Simplicity**: Easy to understand and maintain
- **Lightweight**: Runs on modest hardware
- **Privacy**: Local-first, no cloud dependencies
- **Practicality**: Solves real expense tracking needs

## Questions?

Open an issue for questions or discussions!
