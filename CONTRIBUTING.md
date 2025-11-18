# Contributing to Ace Discord Bot

First off, thank you for considering contributing to Ace! It's people like you that make this bot better for everyone.

## Code of Conduct

This project and everyone participating in it is expected to uphold a respectful and harassment-free environment. Please be kind and courteous to others.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (screenshots, code snippets, etc.)
- **Describe the behavior you observed** and what you expected to see
- **Include your Python version** and OS information

Use the bug report template when available.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **Include examples** of how the feature would work

Use the feature request template when available.

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the coding style of the project
3. **Test your changes** thoroughly
4. **Update documentation** if you've made changes to functionality
5. **Ensure your code follows the existing style**
6. **Write clear commit messages**
7. **Submit a pull request**

#### Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Update the README.md if needed
- Add tests if applicable
- Make sure your code doesn't introduce new warnings
- Follow Python PEP 8 style guidelines
- Comment your code where necessary

## Development Setup

1. Clone your fork of the repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Ace.git
   cd Ace
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file as described in README.md

4. Run the bot locally to test your changes:
   ```bash
   python ace.py
   ```

## Coding Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) Python style guidelines
- Use meaningful variable and function names
- Add comments to explain complex logic
- Keep functions focused and concise
- Use type hints where appropriate

## Database Changes

If your contribution involves database schema changes:

1. Create a new migration file in the `migrations/` directory
2. Follow the existing naming convention (V#_description.sql)
3. Document the changes in your pull request

## Testing

Before submitting your pull request:

- Test your changes with different Discord server configurations
- Verify that existing functionality still works
- Check for any error messages or warnings
- Test edge cases and error handling

## Questions?

Feel free to create an issue with your question or reach out through the Discord support server.

## License

By contributing to Ace, you agree that your contributions will be licensed under the MIT License.
