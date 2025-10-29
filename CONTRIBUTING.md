# Contributing to EvalMate

We love your input! We want to make contributing to EvalMate as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests Process

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## 🐛 Report bugs using GitHub's [issue tracker](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/issues/new).

### Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## 🔧 Development Setup

1. Clone your fork of the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Install development dependencies: `pip install -r requirements-dev.txt`
6. Set up pre-commit hooks: `pre-commit install`

### Code Style

- We use [Black](https://black.readthedocs.io/) for Python code formatting
- We use [isort](https://pycqa.github.io/isort/) for import sorting
- We use [flake8](https://flake8.pycqa.org/) for linting
- All code should be type-hinted using Python's typing module

### Testing

- Write tests for new features
- Ensure all tests pass: `python -m pytest`
- Maintain code coverage above 80%

### Commit Messages

Use clear and meaningful commit messages:

```
feat: add new AI evaluation algorithm
fix: resolve PDF parsing issue with special characters
docs: update API documentation
test: add tests for semantic evaluation
refactor: improve code structure in evaluation service
```

## 📋 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team at conduct@evalmate.ai.

## 🤝 Any contributions you make will be under the MIT Software License

When you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project.

## 📞 Contact

Feel free to contact the maintainers if you have any questions:

- Email: maintainers@evalmate.ai
- Discord: [EvalMate Community](https://discord.gg/evalmate)
- GitHub Issues: [Create an issue](https://github.com/yashvini-chirri/EvalMate-AI-Evaluation/issues/new)

## 🙏 Recognition

Contributors will be recognized in our README and releases. We appreciate every contribution, no matter how small!

Thank you for contributing to EvalMate! 🎉