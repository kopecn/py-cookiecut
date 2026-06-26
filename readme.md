# Cookiecutter PyPackage

A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for bootstrapping a modern Python package.

-   **GitHub**: [kopecn/py-cookiecut](https://github.com/kopecn/py-cookiecut/)
-   **License**: MIT

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
   This template uses a **`dev`/`prod`** branch model. Merge to `prod` to trigger
   `tag-on-prod.yml`, which auto-creates a `v<version>` tag; the (scaffolded) `publish.yml`
   workflow then promotes that tagged build to PyPI once you wire its credentials.

## Suggestions / Forking?

- **Fork freely**: Customize the template to your needs.  This project was originally based on [Audrey's cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage/).
- **Contribute via pull request**: Small, atomic PRs that improve the packaging experience are welcome!  Thanks Audrey. 
