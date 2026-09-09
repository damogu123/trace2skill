# GitHub Preparation Checklist

Use this checklist before publishing the project.

## 1. Verify The Clean Repository View

From the project root:

```powershell
git init
git status --ignored
```

Confirm that these are ignored:

- `runs/`
- `workspaces/`
- `logs/`
- `data/external/`
- `prompts/runs/`
- `paper/*.pdf`
- `paper/svg-inkscape/`
- `results/*.png`

The project-page media under `docs/static/` is intentionally retained,
including its camera-ready PDF and social-preview PNG.

## 2. Validate Structured Artifacts

```powershell
python scripts/validate_task.py tasks
python scripts/validate_trajectory.py trajectories
python scripts/validate_run_manifest.py manifests
```

## 3. Decide What To Release Separately

Recommended GitHub release or external archive attachments:

- final PDF, such as `paper/main_agenticdev.pdf`;
- raw `runs/` directory if reviewers need full execution logs;
- a compressed copy of `data/external/` only if redistribution is allowed;
- rendered inspection screenshots if they are useful for review history.

## 4. Add Repository Metadata

Before making the repository public:

- choose and add a `LICENSE`;
- add citation metadata if desired, for example `CITATION.cff`;
- decide whether the initial repository should be anonymous for review;
- remove or postpone non-anonymous metadata if the venue requires double-blind
  review.

## 5. Optional: Use The Export Directory

This workspace can generate `github_export/`, a clean copy that excludes large
local artifacts. It is intended for initializing a separate Git repository:

```powershell
python scripts/create_github_export.py --force
cd github_export
git init
git status
```

If you commit from the project root instead, rely on the root `.gitignore`.

## 6. Publish The Project Page

The static project page is rooted at `docs/index.html`. After pushing the clean
repository to GitHub:

1. Open repository **Settings > Pages**.
2. Under **Build and deployment**, select **Deploy from a branch**.
3. Select the default branch and the `/docs` folder, then save.
4. Verify `https://damogu123.github.io/trace2skill/` after deployment finishes.

Do not add HotCRP, conference-publishing, or ACM rights-form authorization URLs
to the page or repository.
