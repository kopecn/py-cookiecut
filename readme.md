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

## Template variables

You'll be prompted for these during the bake (each prompt carries inline help via the
`__prompts__` block in `cookiecutter.json`). Two casings apply, and `pre_gen_project.py`
enforces both before rendering:

- `projectIdentifier` — the distribution name, the project folder, and the GitHub repo slug —
  must be **lowercase kebab-case** (`python-boilerplate`). Underscores and uppercase are
  rejected.
- `packageName` and `moduleName` — the **import surface** — must be **PEP-8 snake_case**
  (`my_package`). Hyphens are rejected: they are not legal Python identifiers.

The hook **validates and aborts; it never rewrites your input.** A bad value fails the bake with
a corrective message rather than being silently converted.

| Variable | Convention | Becomes | Example |
|---|---|---|---|
| `fullName` | free text | `LICENSE` + pyproject authors | `Nicholas Bergantz` |
| `email` | email | pyproject authors / PyPI contact | `you@example.com` |
| `githubUsername` | lowercase | repo + issue URLs | `kopecn` |
| `projectName` | Title Case or kebab | README/docs headings **only** — does not set the folder name | `Python Boilerplate` |
| `projectIdentifier` | **kebab-case** | dist name + project folder + GitHub repo slug (`pyproject [project].name`) | `python-boilerplate` |
| `packageName` | **snake_case** | `src/<packageName>/` — what you `import` | `my_package` |
| `moduleName` | **snake_case** | `src/<packageName>/<moduleName>.py` | `my_module` |
| `projectShortDescription` | free text | pyproject `[project].description` | — |
| `pypiUsername` | lowercase | PyPI contact (defaults to `githubUsername`) | `kopecn` |
| `version` | PEP 440 | initial `[project].version` | `0.0.1` |
| `ghIdentifier` | derived | `owner/repo` for GitHub URLs (accept default) | — |

> Note: the cookiecutter variable **keys** are camelCase (`projectIdentifier`) — a
> tooling-internal house style — but the **values** are not: the distribution/folder/repo name
> is kebab-case and the import surface is snake_case.

> **One name, three surfaces.** The generated folder, `pyproject [project].name`, and the GitHub
> repo slug are all the same string. That is deliberate: `git clone` creates a directory named
> after the repo, so if they diverged, a contributor would land in a differently-named directory
> than the bake produced.

## Suggestions / Forking?

- **Fork freely**: Customize the template to your needs.  This project was originally based on [Audrey's cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage/).
- **Contribute via pull request**: Small, atomic PRs that improve the packaging experience are welcome!  Thanks Audrey. 
