# Vantro Safe Declutter Manifest

Date: 2026-06-30

## Kept

- Source code, migrations, tests, app routes, runtime modules, and frontend pages.
- Launch docs, session reports, specs, runbooks, and env examples.
- `.superpowers/sdd/progress.md`, because it is tracked project state.

## Removed

- Root-level UI/debug screenshots:
  - `admin-login-attempt.png`
  - `admin-login-screenshot.png`
  - `create-media-expanded.png`
  - `create-media-format-grid.png`
  - `create-media-tightened.png`
  - `screenshot.png`
- One-off report placeholder:
  - `TASK_1_REPORT.md`
- Generated frontend/infra artifacts:
  - `frontend/tsconfig.tsbuildinfo`
  - `frontend/filename.txt`
  - `terraform/tfplan`
  - `terraform/apply.log`
- Generated `.superpowers/sdd` review/task scratch files:
  - `final-review-fix-report.md`
  - `review-*.diff`
  - `task-*-brief.md`
  - `task-*-report.md`

## Ignore Rules Added

- Root screenshots/debug captures.
- TypeScript incremental build cache.
- Terraform plan and apply logs.
- `.superpowers/sdd` transient review/task scratch files.

## Stale Site References Normalized

- Removed references to prior public-site variants from the admin media routing session report.
- Normalized stale public/web defaults to current Vantro surfaces:
  - Public site: `https://vantro.ai`
  - Admin site: `https://admin.vantro.ai`
  - API site: `https://api.vantro.ai`
- Kept generic client deliverable wording such as "landing page" where it describes what agents can create for customers rather than an old Vantro public site.

## Safety Notes

- No source, test, migration, production config template, or launch handover document was removed.
- Cleanup was limited to files that are generated, local, visual debug evidence, or stale task scratch output.
