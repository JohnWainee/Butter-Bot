# Butter-Bot

Automated documentation creator and maintainer across multiple platforms,
languages, and services.

Butter-Bot generates and updates runbooks, architecture overviews, module
deep dives, and IBM style compliance reports for your repositories. It ships
as a shared Python core with an MCP server frontend, and adds a CLI and
GitHub Action frontend later.

## Project status

Pre-release. The project plan and architecture decisions are approved; the
style engine MVP is next.

- [Project plan](docs/plan/butter-bot-plan.md)
- [Architecture decision records](docs/adr/)
- [Branch protection settings](docs/process/branch-protection.md)

## Develop

Install the package with development extras, then run the checks:

```bash
pip install -e ".[dev]"
ruff check .
pytest
```
