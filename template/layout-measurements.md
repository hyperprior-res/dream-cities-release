# Layout measurements

Measured on 17 October 2026 before writing the class. The reference PDF and source
archive were read at `https://arxiv.org/pdf/2602.11865` and
`https://arxiv.org/e-print/2602.11865`. They remain outside this output tree. No text,
class implementation, artwork or organisational marks were copied.

`pdfinfo`, `pdffonts` and `pdftotext -bbox-layout` were run before implementation.
Coordinates below are PDF points from the top-left corner; TeX points differ by
the factor 72.27/72. Source inspection confirmed the nominal settings.

| Element | Measured or specified value |
|---|---|
| Page | A4, 595.276 × 841.890 PDF pt |
| Side margins | 22 mm; left text edge 62.362 PDF pt |
| Top and bottom margins | 30 mm |
| Full text width | 470.552 PDF pt, 6.5354 in |
| Column gap | 15 TeX pt, 14.944 PDF pt |
| Column width | 227.804 PDF pt, 3.1639 in |
| Header height and separation | 40 TeX pt and 20 TeX pt |
| Main text | XCharter Roman, nominal 11 TeX pt |
| Paragraph spacing | Half a baseline; first-line indentation retained |
| Title | XCharter Bold, 21/23 TeX pt; ink top 88.018 PDF pt |
| Authors | XCharter Bold, 9/13 TeX pt; ink top 120.918 PDF pt |
| Affiliation | XCharter Roman, 8/10 TeX pt; ink top 132.221 PDF pt |
| Title-to-author space | 11 TeX pt |
| Abstract | XCharter Bold, 10/12 TeX pt, line spread 1.2; ink top 162.459 PDF pt |
| Abstract width | Full text width |
| Keywords | XCharter Italic, 11/12 TeX pt, line spread 1.2 |
| First section | Bold 13/14 TeX pt, number followed by full stop |
| Subsections | Bold body size; subsubsections bold italic |
| Heading spaces | Section 3 ex above and 5 pt below; subsection 2.5 ex and 2 pt |
| First-page mark | 18 TeX pt high in upper-left header |
| Date | Upper right, italic 8/10 TeX pt; ink top 55.312 PDF pt |
| Other-page header | Centred paper title, 8/10 TeX pt |
| Footer | First-page correspondence and copyright on separate lines; later pages numbered at right |
| Rules | 1 TeX pt grey header and footer rules |
| Captions | Body size, left aligned, normal-weight label, vertical-bar separator |
| Tables | Horizontal rules; no mandatory vertical rules |
| References | Author–year citations, abbreviated-name bibliography, hanging entries |
| Fonts in reference | XCharter Roman, Bold, Italic and BoldItalic; XCharter mathematics; Latin Modern Mono |

The reference also contains one unembedded base font. The reconstruction does not
retain that defect: all output fonts must be embedded, with no bitmap Type 3.
The class is an independent implementation of these measurements.

The Austin wordmark is generated from the website font as outlined SVG and PDF
paths. Its nominal tracking is −0.055 em, and its colour is `#8E1B1E`. No live font
is embedded in the mark. The reference-page comparison hides its correspondence
line and removes its margin identifier before rendering. The unsanitised page is
never included in tracked output.
