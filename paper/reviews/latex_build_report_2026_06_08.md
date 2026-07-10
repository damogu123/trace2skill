# LaTeX Build Report

Date: 2026-06-08

## Environment

- MiKTeX 25.12, updated to the current package set
- pdfTeX/BibTeX from MiKTeX 26.5
- latexmk 4.88
- Strawberry Perl 5.42.2.1
- Inkscape 1.4.4

## Build

Command, run from `paper/`:

```powershell
latexmk -pdf -shell-escape -interaction=nonstopmode -file-line-error main.tex
```

Result:

- output: `paper/main_figures_clean.pdf`
- pages: 20
- page size: US Letter
- bibliography: 18 entries resolved through BibTeX
- SVG figures: 4/4 converted and embedded
- final LaTeX/BibTeX log scan: no overfull/underfull boxes, undefined
  citations, undefined references, package warnings, or BibTeX warnings

`paper/main.pdf` was open and locked by a PDF viewer during the final build, so
it could not be overwritten. It remains the earlier 22-page build.

## Corrections Made During Build

- enabled Latin Modern scalable fonts for microtype compatibility;
- disabled the SVG LaTeX text overlay so underscores in figure labels compile
  safely;
- constrained both result tables to the text width;
- made long code-style identifiers breakable;
- added float barriers and fixed placement for the two main result tables;
- removed the redundant ExpeL issue field that caused a BibTeX style warning.
- changed citations to bracketed numeric references ordered by first appearance;
- disabled numeric-range compression so multi-source citations render as
  `[3, 4, 5]` rather than `[3--5]` before a venue template is selected;
- replaced Latin Modern with the Times-style `newtxtext`/`newtxmath` family so
  citation markers such as `[1]` have the wider, more compact proportions
  common in computer-science conference papers;
- increased Figure 2 titles, axis labels, tick labels, values, and method
  labels for print readability;
- increased Figure 3 titles, axes, ticks, marker labels, and legend text, and
  separated the x-axis title from the marker-size/efficiency note.
- removed the redundant marker-size/efficiency note from inside Figure 3;
  these encodings are now explained only in the figure caption.
- rerouted Figure 1 control-condition connectors and enlarged the metric box;
- replaced Figure 3 point labels with compact letter markers and a separate
  method legend.

Rendered checks covered the title/abstract page, Method protocol figure,
Results tables and figures, declarations, and bibliography pages.
