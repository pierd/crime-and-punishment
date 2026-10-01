#!/usr/bin/env python3
"""
Convert Project Gutenberg HTML to LaTeX, split into 6 books.
"""

import re
from pathlib import Path

HTML_FILE = Path("project-gutenberg-text.html")
OUTPUT_DIR = Path("latex_output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Read the HTML file
with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Remove Project Gutenberg header (everything before the main content)
# The content starts after the START separator
start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK CRIME AND PUNISHMENT ***"
end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK CRIME AND PUNISHMENT ***"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1 or end_idx == -1:
    raise ValueError("Could not find start/end markers")

# Extract content between markers
content = html[start_idx + len(start_marker):end_idx]

# Clean up HTML entities
content = content.replace("&mdash;", "---")
content = content.replace("&nbsp;", " ")
content = content.replace("&", "&")
content = content.replace("<", "<")
content = content.replace(">", ">")
content = content.replace("&ldquo;", '"')
content = content.replace("&rdquo;", '"')
content = content.replace("&lsquo;", "'")
content = content.replace("&rsquo;", "'")
content = content.replace("&#8212;", "---")
content = content.replace("&#8216;", "'")
content = content.replace("&#8217;", "'")
content = content.replace("&#8220;", '"')
content = content.replace("&#8221;", '"')
content = content.replace("&#160;", " ")

# Remove anchor links and IDs
content = re.sub(r'<a\s+id="[^"]*"\s*>\s*</a>', '', content)
content = re.sub(r'<a\s+href="#[^"]*"\s+class="pginternal">([^<]*)</a>', r'\1', content)
content = re.sub(r'<a\s+class="reference external"\s+href="[^"]*">([^<]*)</a>', r'\1', content)

# Convert HTML tags to LaTeX
# Headers - handle all h2 variants (with class, with anchor, plain)
content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\\part*{\1}', content, flags=re.DOTALL)
content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\\chapter*{\1}', content, flags=re.DOTALL)
content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\\section*{\1}', content, flags=re.DOTALL)
content = re.sub(r'<h4[^>]*>(.*?)</h4>', r'\\subsection*{\1}', content, flags=re.DOTALL)
content = re.sub(r'<h5[^>]*>(.*?)</h5>', r'\\subsubsection*{\1}', content, flags=re.DOTALL)

# Horizontal rule
content = re.sub(r'<hr\s*/?>', r'\\bigskip\\hrule\\bigskip', content)

# Remove the table of contents section (we'll generate our own)
content = re.sub(r'<div style="font-size: large"><b>CONTENTS</b></div>.*?(?=<div class="chapter">)', '', content, flags=re.DOTALL)

# Remove unwanted title elements: "CRIME AND PUNISHMENT", "By Fyodor Dostoevsky", "Translated By Constance Garnett"
content = re.sub(r'\\(?:part|chapter)\*\{[^}]*CRIME AND PUNISHMENT[^}]*\}', '', content)
content = re.sub(r'\\chapter\*\{[^}]*By Fyodor Dostoevsky[^}]*\}', '', content)
content = re.sub(r'\\chapter\*\{[^}]*Translated By Constance Garnett[^}]*\}', '', content)
content = re.sub(r'\\section\*\{[^}]*Translated By Constance Garnett[^}]*\}', '', content)

# Paragraphs
content = re.sub(r'<p class="poem">(.*?)</p>', r'\\begin{verse}\1\\end{verse}', content, flags=re.DOTALL)
content = re.sub(r'<p class="noindent">(.*?)</p>', r'\\noindent \1\\par', content, flags=re.DOTALL)
content = re.sub(r'<p class="footnote">(.*?)</p>', r'\\footnote{\1}', content, flags=re.DOTALL)
content = re.sub(r'<p>(.*?)</p>', r'\1\\par', content, flags=re.DOTALL)

# Bold and italic
content = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', content)
content = re.sub(r'<i>(.*?)</i>', r'\\textit{\1}', content)
content = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', content)
content = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', content)

# Line breaks
content = re.sub(r'<br\s*/?>', r'\\newline ', content)

# Div chapters
content = re.sub(r'<div class="chapter">\s*', '', content)
content = re.sub(r'</div>\s*<!--end chapter-->', '', content)
content = re.sub(r'</div>', '', content)

# Remove any remaining HTML tags
content = re.sub(r'<[^>]+>', '', content)

# Clean up whitespace
content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
content = content.strip()

# Now split into sections based on chapter markers
# Find all chapter/part markers
chapter_pattern = r'\\chapter\*\{([^}]+)\}'
chapters = list(re.finditer(chapter_pattern, content))

# Define split points
# Book 1: Translator's Preface + PART I (up to PART II)
# Book 2: PART II
# Book 3: PART III
# Book 4: PART IV
# Book 5: PART V
# Book 6: PART VI + EPILOGUE

book_titles = [
    "Translator's Preface and Part I",
    "Part II",
    "Part III",
    "Part IV",
    "Part V",
    "Part VI and Epilogue"
]

# Find positions of each part
part_positions = {}
for m in chapters:
    title = m.group(1).strip()
    pos = m.start()
    if title in ["TRANSLATOR'S PREFACE", "PART I", "PART II", "PART III", "PART IV", "PART V", "PART VI", "EPILOGUE"]:
        part_positions[title] = pos

# Also find CRIME AND PUNISHMENT title
crime_title_match = re.search(r'\\part\*\{CRIME AND PUNISHMENT\}', content)
if crime_title_match:
    part_positions["CRIME AND PUNISHMENT"] = crime_title_match.start()

# Sort by position
sorted_parts = sorted(part_positions.items(), key=lambda x: x[1])

# Print for debugging
for title, pos in sorted_parts:
    print(f"  {title}: position {pos}")

# Define book boundaries
books = [
    # Book 1: From start to PART II
    ("book1", 0, part_positions.get("PART II", len(content))),
    # Book 2: PART II to PART III
    ("book2", part_positions.get("PART II", 0), part_positions.get("PART III", len(content))),
    # Book 3: PART III to PART IV
    ("book3", part_positions.get("PART III", 0), part_positions.get("PART IV", len(content))),
    # Book 4: PART IV to PART V
    ("book4", part_positions.get("PART IV", 0), part_positions.get("PART V", len(content))),
    # Book 5: PART V to PART VI
    ("book5", part_positions.get("PART V", 0), part_positions.get("PART VI", len(content))),
    # Book 6: PART VI to end
    ("book6", part_positions.get("PART VI", 0), len(content)),
]

# LaTeX template
latex_preamble = (
    "\\documentclass[12pt,twoside,openany,a5paper]{book}\n"
    "\\usepackage[utf8]{inputenc}\n"
    "\\usepackage[T1]{fontenc}\n"
    "\\usepackage{lmodern}\n"
    "\\usepackage{geometry}\n"
    "\\geometry{margin=0.75in}\n"
    "\\usepackage{setspace}\n"
    "\\onehalfspacing\n\n"
    "% Simple chapter/section formatting without titlesec\n"
    "\\makeatletter\n"
    "\\renewcommand\\part{%\n"
    "  \\if@openright\n"
    "    \\cleardoublepage\n"
    "  \\else\n"
    "    \\clearpage\n"
    "  \\fi\n"
    "  \\thispagestyle{plain}%\n"
    "  \\if@twocolumn\n"
    "    \\onecolumn\n"
    "    \\@tempswatrue\n"
    "  \\else\n"
    "    \\@tempswafalse\n"
    "  \\fi\n"
    "  \\null\\vfil\n"
    "  \\secdef\\@part\\@spart}\n"
    "\\def\\@part[#1]#2{%\n"
    "  \\ifnum \\c@secnumdepth >-2\\relax\n"
    "    \\refstepcounter{part}%\n"
    "    \\addcontentsline{toc}{part}{\\thepart\\hspace{1em}#1}%\n"
    "  \\else\n"
    "    \\addcontentsline{toc}{part}{#1}%\n"
    "  \\fi\n"
    "  {\\centering\n"
    "   \\interlinepenalty \\@M\n"
    "   \\normalfont\n"
    "   \\huge \\bfseries #2%\n"
    "   \\markboth{}{}\\par}\n"
    "  \\nobreak\n"
    "  \\vskip 3ex\n"
    "  \\@afterheading}\n"
    "\\def\\@spart#1{%\n"
    "  {\\centering\n"
    "   \\interlinepenalty \\@M\n"
    "   \\normalfont\n"
    "   \\huge \\bfseries #1%\n"
    "   \\markboth{}{}\\par}\n"
    "  \\nobreak\n"
    "  \\vskip 3ex\n"
    "  \\@afterheading}\n"
    "\\renewcommand\\chapter{%\n"
    "  \\if@openright\\cleardoublepage\\else\\clearpage\\fi\n"
    "  \\thispagestyle{plain}%\n"
    "  \\global\\@topnum\\z@\n"
    "  \\@afterindentfalse\n"
    "  \\secdef\\@chapter\\@schapter}\n"
    "\\def\\@chapter[#1]#2{%\n"
    "  \\ifnum \\c@secnumdepth >\\m@ne\n"
    "    \\refstepcounter{chapter}%\n"
    "    \\addcontentsline{toc}{chapter}{\\protect\n"
    "      \\numberline{\\thechapter}#1}%\n"
    "  \\else\n"
    "    \\addcontentsline{toc}{chapter}{#1}%\n"
    "  \\fi\n"
    "  {\\centering\\normalfont\\Large\\bfseries #2\\par}\n"
    "  \\nobreak\n"
    "  \\vskip 1.5ex\n"
    "  \\@afterheading}\n"
    "\\def\\@schapter#1{%\n"
    "  {\\centering\\normalfont\\Large\\bfseries #1\\par}\n"
    "  \\nobreak\n"
    "  \\vskip 1.5ex\n"
    "  \\@afterheading}\n"
    "\\makeatother\n\n"
    "\\begin{document}\n"
)

latex_postamble = "\\end{document}\n"

def make_title_page(book_num, book_title):
    return (
        "\\thispagestyle{empty}\n"
        "\\vspace*{3cm}\n"
        "\\begin{center}\n"
        "{\\Huge \\bfseries Crime and Punishment}\\\\[1cm]\n"
        "{\\Large by Fyodor Dostoevsky}\\\\[0.5cm]\n"
        "{\\normalsize Translated by Constance Garnett}\\\\[3cm]\n"
        "{\\LARGE " + book_title + "}\\\\[2cm]\n"
        "{\\large Book " + str(book_num) + " of 6}\n"
        "\\end{center}\n"
        "\\vfill\n"
        "\\clearpage\n"
    )

# Write each book
for i, (book_name, start, end) in enumerate(books):
    book_content = content[start:end].strip()
    book_title = book_titles[i]

    latex = latex_preamble
    latex += make_title_page(i+1, book_title)
    latex += book_content
    latex += "\n" + latex_postamble

    output_file = OUTPUT_DIR / f"{book_name}.tex"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(latex)

    print(f"Written: {output_file}")

print("\nDone! Now compile with: cd latex_output && pdflatex book1.tex (run 2-3 times for TOC)")