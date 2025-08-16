# Cookiecutter PyPackage

[![PyPI version](https://img.shields.io/pypi/v/TBD.svg)](https://pypi.python.org/pypi/TBD)
[![PyPI downloads](https://img.shields.io/pypi/dm/TBD.svg)](https://pypi.python.org/pypi/TBD)

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for bootstrapping a modern Python package.

-   **GitHub**: [kopecn/py-cookiecut](https://github.com/kopecn/py-cookiecut/)
-   **License**: MIT
-   **Discord**: [Join the community](https://discord.gg/TBD)

---

## 🚀 Features

-   ✅ Testing setup with **pytest**
-   🔁 GitHub Actions CI for **Python 3.10 – 3.13**
-   📦 Auto-release to [PyPI](https://pypi.python.org/pypi) via tag push (optional)
-   🖥️ CLI support via **Typer**

---

## ⚡ Quickstart

### 1. Install Cookiecutter

```bash
pip install -U cookiecutter
```

Generate a Python package project:

```bash
cookiecutter https://github.com/kopecn/py-cookiecut.git
```

Then:

1. **Create a GitHub repository**  
   Push your newly generated project to a GitHub repo.

2. **Register your project with PyPI**  
   Follow the [official guide](https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives) to upload your distribution archives.

3. **Set up documentation on Read the Docs**  
   Add your repository to your [Read the Docs](https://readthedocs.io/) account and enable the service hook for automated builds.

4. **Release your package**  
   Push a new Git tag to the `master` branch to trigger an automatic release to PyPI (if configured).

## Suggestions / Forking?

- **Fork freely**: Customize the template to your needs. This project was originally based on [Audrey's cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage/).
- **Contribute via pull request**: Small, atomic PRs that improve the packaging experience are welcome!  Thanks Audrey. 
