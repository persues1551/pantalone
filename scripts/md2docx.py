#!/usr/bin/env python3
"""
Markdown to Word document converter.
Usage: python3 md2docx.py input.md output.docx

Features:
- Headers (H1-H4) mapped to Word heading styles
- Tables auto-detected and formatted as Word tables
- Code blocks rendered in Courier New 9pt
- Blockquotes indented
- Bold text preserved
- Bullet/numbered lists mapped to Word list styles

Requires: python-docx (pip install python-docx)
"""
import sys
import re
from docx import Document
from docx.shared import Pt, Inches


def md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Microsoft YaHei'
    style.font.size = Pt(11)

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Headers
        if line.startswith('##### '):
            doc.add_heading(line[6:], level=4)
        elif line.startswith('#### '):
            doc.add_heading(line[5:], level=3)
        elif line.startswith('### '):
            doc.add_heading(line[4:], level=2)
        elif line.startswith('## '):
            doc.add_heading(line[3:], level=1)
        elif line.startswith('# '):
            doc.add_heading(line[2:], level=0)

        # Tables
        elif '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                if '---' not in lines[i]:
                    table_lines.append(lines[i])
                i += 1
            i -= 1
            if len(table_lines) > 1:
                def parse_table_row(value):
                    value = value.strip()
                    if value.startswith('|'):
                        value = value[1:]
                    if value.endswith('|'):
                        value = value[:-1]
                    return [cell.strip() for cell in value.split('|')]

                headers = parse_table_row(table_lines[0])
                rows = []
                for tl in table_lines[1:]:
                    row = parse_table_row(tl)
                    if row:
                        rows.append(row)
                if headers and rows:
                    mismatched = [index + 1 for index, row in enumerate(rows) if len(row) != len(headers)]
                    try:
                        if mismatched:
                            raise ValueError(f"row column mismatch at data rows {mismatched}")
                        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
                        table.style = 'Table Grid'
                        for j, h in enumerate(headers):
                            if j < len(table.rows[0].cells):
                                table.rows[0].cells[j].text = h
                        for j, row in enumerate(rows):
                            for k, cell in enumerate(row):
                                if k < len(table.rows[j + 1].cells):
                                    table.rows[j + 1].cells[k].text = cell
                        doc.add_paragraph('')
                    except Exception as exc:
                        print(f"WARNING: malformed markdown table near line {i + 1}: {exc}", file=sys.stderr)
                        for tl in table_lines:
                            if tl.strip():
                                doc.add_paragraph(tl.strip())

        # Code blocks
        elif line.startswith('```'):
            code_block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_block.append(lines[i])
                i += 1
            if code_block:
                p = doc.add_paragraph()
                run = p.add_run('\n'.join(code_block))
                run.font.name = 'Courier New'
                run.font.size = Pt(9)

        # Blockquotes
        elif line.startswith('>'):
            p = doc.add_paragraph(line[1:].strip())
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)

        # Horizontal rules
        elif line.startswith('---'):
            doc.add_paragraph('')

        # Bullet lists
        elif line.startswith('- ') or line.startswith('* '):
            doc.add_paragraph(line[2:], style='List Bullet')

        # Numbered lists
        elif re.match(r'^\d+\.', line):
            doc.add_paragraph(line, style='List Number')

        # Bold text
        elif '**' in line:
            p = doc.add_paragraph()
            parts = line.split('**')
            for j, part in enumerate(parts):
                if j % 2 == 0:
                    p.add_run(part)
                else:
                    run = p.add_run(part)
                    run.bold = True

        # Normal text
        elif line:
            doc.add_paragraph(line)

        i += 1

    doc.save(docx_path)
    print(f'Word文档已生成: {docx_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} input.md output.docx')
        sys.exit(1)
    md_to_docx(sys.argv[1], sys.argv[2])
