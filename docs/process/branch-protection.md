# Branch protection settings

Apply these settings to `main` in the repository settings on GitHub.
GitHub free plans enforce branch protection on public repositories.

## Required settings

- Require a pull request before merging.
- Require status checks to pass: select the `lint-and-test` check from the
  CI workflow.
- Require branches to be up to date before merging.
- Block force pushes.

## Recommended settings

- Require conversation resolution before merging.
- Dismiss stale approvals when new commits are pushed.

## Workflow

Work follows this flow: issue, branch, plan, verify, PR, review, merge.
Use conventional commit messages, for example `feat(style): add serial
comma rule`.
