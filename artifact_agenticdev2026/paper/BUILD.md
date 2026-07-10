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
