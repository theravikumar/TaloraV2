# Contributing to TaloraV2

Thank you for contributing! This guide will help you get started.

## Getting Started

1. **Fork and clone**
   ```bash
   git clone <your-fork-url>
   cd TaloraV2
   ```

2. **Set up development environment**
   ```bash
   uv sync
   cp .env.example .env
   # Add your API keys to .env
   ```

3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## What to Work On

Check our [GitHub Issues](https://github.com/your-repo/issues) for:
- Good first issues (labeled `good-first-issue`)
- Bug reports (labeled `bug`)
- Feature requests (labeled `enhancement`)

## Code Guidelines

### Python Style
- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions focused (< 50 lines)

### Example
```python
def normalize_resume(pdf_path: str) -> Dict:
    """
    Extract structured data from PDF resume.
    
    Args:
        pdf_path: Absolute path to PDF file
        
    Returns:
        Dictionary with name, skills, work_units, etc.
    """
    # Implementation
    pass
```

### File Organization
- One class per file (generally)
- Keep related functions together
- Use meaningful file names

### No Emojis in Code
- OK in comments for teammates
- Not in production strings or logs
- Not in variable/function names

## Testing Your Changes

### Before Committing

1. **Test your code**
   ```bash
   # Run relevant tests
   uv run pytest tests/test_your_feature.py
   ```

2. **Test integration**
   ```bash
   # Run full demo
   uv run python scripts/demo_resume_matching.py data/resumes/ravi_resume_9608676321.pdf
   ```

3. **Check it works with different inputs**
   ```bash
   # Try different resumes
   # Try different job searches
   ```

## Commit Messages

Use conventional commits:

```
feat: add new job source (RemoteOK)
fix: handle PDF extraction errors
docs: update ARCHITECTURE.md with new flow
refactor: simplify work unit matcher
test: add tests for job normalizer
```

## Pull Request Process

1. **Update documentation** if you changed behavior
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Create PR** with clear description

### PR Template
```markdown
## What does this PR do?
Brief description

## Why is this needed?
Explain the problem it solves

## How to test?
Steps to verify the changes work

## Screenshots (if UI changes)
Add screenshots if applicable
```

## Areas to Contribute

### Easy (Good for beginners)
- Add new job sources (copy existing scraper pattern)
- Improve documentation
- Add tests
- Fix bugs in scrapers

### Medium
- Improve matching algorithm
- Add new features to resume parser
- Optimize performance
- Add new LLM providers

### Hard
- Build REST API (FastAPI)
- Add user authentication
- Create frontend (React)
- Deploy to production

## Questions?

- Check [DEVELOPMENT.md](DEVELOPMENT.md) first
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for design
- Ask in GitHub Discussions
- Contact team lead: Ravi Kumar

## Code Review

Expect feedback on:
- Code quality and style
- Test coverage
- Documentation
- Performance implications

Be open to suggestions - we're all learning!

## License

By contributing, you agree your code will be licensed under MIT License (or project license).

## Thank You!

Every contribution helps make TaloraV2 better for everyone!
