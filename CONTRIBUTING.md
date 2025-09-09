# Contributing Guidelines

Thanks for considering contributing to this project!
We welcome bug fixes, new features, documentation updates, and other improvements.

## Before you start

If an issue exists, comment there to let the maintainers know you want to work on it.

If no issue exists, [open a new issue](https://github.com/CPSC-383/aegis/issues) to discuss your idea before making changes.
This helps avoid duplicate work and ensures your contribution aligns with the project goals.

## How to Contribute

### 1. Fork the repository

Click the **Fork** button at the top right of this repo's GitHub page.
This creates your own copy under your GitHub account.

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

### 3. Create a new branch

Name your branch according to what you're working on.

```bash
git switch -c <branch-name>
```

Example:

```bash
git switch -c fix/client-rendering
```

### 4. Make your changes

- Keep changes focused. Don't mix unrelated changes in a PR. 
- Follow any coding style rules defined in the repo.
- Run code quality checks before submitting:

For Aegis (Python) code:

```bash
ruff check src
ruff format src
```

For Client (TS) code:

```bash
npx eslint src src-electron
npx prettier --write .
```

Ensure all linting and formatting checks pass before creating your PR.

### 5. Commit your changes

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format.

### 6. Open a Pull Request

- Go to your fork on GitHub.
- You should see *Compare & pull request* button.
- Fill in the PR description.

PR titles must follow the format `<type>(<scope>): <description>` where the description starts with a lowercase letter.

Good Example:

```bash
feat(agent): added new ability
```

Bad Example:

```bash
added agent function
```

### 7. Code review process 

All pull requests require at least one approval from a maintainer.
Reviews may request changes, please address feedback and push updates to the same branch.
Once approved and passing CI, the PR will be merged.
