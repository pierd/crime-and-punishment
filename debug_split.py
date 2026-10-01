#!/usr/bin/env python3
import re

with open('project-gutenberg-text.html', 'r', encoding='utf-8') as f:
    html = f.read()

start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK CRIME AND PUNISHMENT ***"
end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK CRIME AND PUNISHMENT ***"

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)
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
content = re.sub(r'<h1>(.*?)</h1>', r'\\part*{\1}', content)
content = re.sub(r'<h2 class="no-break">(.*?)</h2>', r'\\chapter*{\1}', content)
content = re.sub(r'<h2><a id="[^"]*"></a>\s*(.*?)</h2>', r'\\chapter*{\1}', content)
content = re.sub(r'<h2>(.*?)</h2>', r'\\chapter*{\1}', content)
content = re.sub(r'<h3>(.*?)</h3>', r'\\section*{\1}', content)
content = re.sub(r'<h4>(.*?)</h4>', r'\\subsection*{\1}', content)
content = re.sub(r'<h5>(.*?)</h5>', r'\\subsubsection*{\1}', content)
content = re.sub(r'<hr\s*/?>', r'\\bigskip\\hrule\\bigskip', content)
content = re.sub(r'<p class="poem">(.*?)</p>', r'\\begin{verse}\1\\end{verse}', content, flags=re.DOTALL)
content = re.sub(r'<p class="noindent">(.*?)</p>', r'\\noindent \1\\par', content, flags=re.DOTALL)
content = re.sub(r'<p class="footnote">(.*?)</p>', r'\\footnote{\1}', content, flags=re.DOTALL)
content = re.sub(r'<p>(.*?)</p>', r'\1\\par', content, flags=re.DOTALL)
content = re.sub(r'<b>(.*?)</b>', r'\\textbf{\1}', content)
content = re.sub(r'<i>(.*?)</i>', r'\\textit{\1}', content)
content = re.sub(r'<em>(.*?)</em>', r'\\textit{\1}', content)
content = re.sub(r'<strong>(.*?)</strong>', r'\\textbf{\1}', content)
content = re.sub(r'<br\s*/?>', r'\\newline ', content)
content = re.sub(r'<div class="chapter">\s*', '', content)
content = re.sub(r'</div>\s*<!--end chapter-->', '', content)
content = re.sub(r'</div>', '', content)
content = re.sub(r'<[^>]+>', '', content)

# Remove table of contents
content = re.sub(r'<div style="font-size: large"><b>CONTENTS</b></div>.*?(?=<div class="chapter">)', '', content, flags=re.DOTALL)

content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
content = content.strip()

# Find chapter markers
chapter_pattern = r'\\chapter\*\{([^}]+)\}'
chapters = list(re.finditer(chapter_pattern, content))

part_positions = {}
for m in chapters:
    title = m.group(1).strip()
    pos = m.start()
    if title in ["TRANSLATOR'S PREFACE", "PART I", "PART II", "PART III", "PART IV", "PART V", "PART VI", "EPILOGUE"]:
        part_positions[title] = pos

for title, pos in sorted(part_positions.items(), key=lambda x: x[1]):
    print(f"{title}: {pos}")