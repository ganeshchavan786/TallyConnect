# Contributing to TallyConnect

🎉 Thank you for considering contributing to TallyConnect!

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## 🛠️ How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **System information** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Include:

- **Clear use case**
- **Why this would be useful**
- **Possible implementation** (optional)

### Pull Requests

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit PR with clear description

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/TallyConnect.git
cd TallyConnect

# Install dependencies
pip install -r requirements.txt

# Run the application
python C2.py
```

## 🔄 Pull Request Process

1. **Update Documentation** - If you add features, update README.md
2. **Test Your Changes** - Ensure everything works
3. **Follow Coding Standards** - See below
4. **Clear Commit Messages** - Descriptive commits
5. **One Feature Per PR** - Keep PRs focused

### PR Checklist

- [ ] Code follows project style
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No database files committed
- [ ] Tested on Windows
- [ ] No breaking changes (or documented)

## 📝 Coding Standards

### Python Style

- **PEP 8** compliant
- **Type hints** where appropriate
- **Docstrings** for functions/classes
- **Meaningful variable names**

### Example

```python
def generate_report(company_name: str, start_date: str, end_date: str) -> str:
    """
    Generate HTML report for a company.
    
    Args:
        company_name: Name of the company
        start_date: Start date (DD-MM-YYYY)
        end_date: End date (DD-MM-YYYY)
    
    Returns:
        Path to generated HTML file
    """
    # Implementation
    pass
```

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- First line: brief summary (50 chars)
- Blank line, then detailed description
- Reference issues: "Fixes #123"

### Examples

```
Add HTML report generation feature

- Implement beautiful HTML templates
- Add export to PDF functionality
- Include search and filter options

Fixes #45
```

## 🎨 UI/UX Guidelines

- **Consistency** - Follow existing design patterns
- **Accessibility** - Clear labels, good contrast
- **Performance** - Keep UI responsive
- **Themes** - Test with all 5 themes

## 🐛 Bug Fix Process

1. Create issue (if doesn't exist)
2. Fork & create branch: `fix/issue-123-bug-description`
3. Fix the bug
4. Add test case (if possible)
5. Submit PR referencing issue

## ✨ Feature Addition Process

1. Discuss in issue first (for major features)
2. Fork & create branch: `feature/feature-name`
3. Implement feature
4. Update documentation
5. Submit PR with demo/screenshots

## 📦 Building & Testing

### Build Executable

```bash
python -m PyInstaller TallyConnect.spec
```

### Test Installer

```bash
# Compile with Inno Setup
iscc TallyConnectInstaller.iss
```

## 🌐 Community

- **Issues**: Bug reports & feature requests
- **Discussions**: General questions & ideas
- **Pull Requests**: Code contributions

## 📞 Contact

- GitHub: [@ganeshchavan786](https://github.com/ganeshchavan786)
- Repository: [TallyConnect](https://github.com/ganeshchavan786/TallyConnect)

---

**Thank you for contributing! 🙏**

