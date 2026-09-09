# AgenticDev 2026 manuscript build

The manuscript targets the AgenticDev 2026 Full Paper track and uses the
anonymous ACM proceedings format:

```latex
\documentclass[sigconf,review,anonymous,pbalance]{acmart}
```

The Windows development environment contains MiKTeX, Strawberry Perl,
Inkscape, and the ACM `acmart`/`pbalance` packages.

Build from `paper/`:

```powershell
$env:Path="C:\Strawberry\perl\bin;C:\Strawberry\c\bin;$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;C:\Program Files\Inkscape\bin;$env:Path"
latexmk -pdf -jobname=main_agenticdev -shell-escape -interaction=nonstopmode -file-line-error main.tex
```

The `-shell-escape` option is required because the manuscript converts SVG
figures through Inkscape. The verified output is
`paper/main_agenticdev.pdf`: 10 pages of manuscript content followed by one
references-only page.

To clean generated files while retaining source and the final PDF:

```powershell
latexmk -c -jobname=main_agenticdev main.tex
```

## Two-page poster camera-ready draft

The accepted poster-paper source is `main_poster.tex`. It uses the
non-anonymous ACM `sigconf,screen,pbalance` format, `microtype`, the final ACM
eRights metadata, and the public artifact URL.

Build from `paper/`:

```powershell
$env:Path="C:\Strawberry\perl\bin;C:\Strawberry\c\bin;$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;C:\Program Files\Inkscape\bin;$env:Path"
latexmk -g -pdf -interaction=nonstopmode -halt-on-error -jobname=agenticdev2026_paper12_camera_ready main_poster.tex
```

The upload-ready output `paper/agenticdev2026_paper12_camera_ready.pdf` is two
US Letter pages. The older `paper/main_poster.pdf` is superseded and may remain
locked by the PDF viewer. The final eRights block was inserted on September 9,
2026: CC-BY, DOI
`10.1145/3843282.3844421`, ISBN `979-8-4007-2985-0/2026/10`, and proceedings
dates `October 12--16, 2026`. Do not replace these values with the earlier
HotCRP placeholders.

The paper-specific author instructions also require submission ID
`asews26agenticdevmain-p12-p`, received/accepted dates, corresponding-author
status, ORCID, default-size table and figure text, and an unframed figure.
These requirements were applied and verified on September 9, 2026. See
`submission/agenticdev_camera_ready_compliance_checklist.md`.

The source upload is `submission/agenticdev_camera_ready_source.zip`. It
contains `main.tex`, `references.bib`, `main.bbl`, `acmart.cls` v2.18, and
`ACM-Reference-Format.bst`; an isolated extraction rebuilds the same article
text. Paste `submission/agenticdev_ccs.xml` into the CCS XML form field.
