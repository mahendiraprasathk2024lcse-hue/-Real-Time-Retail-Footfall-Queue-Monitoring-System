# report_builder/styles.py
"""
Document styling and layout configuration for academic project report.
Follows university engineering project report standards:
- Paper: A4 (8.27 x 11.69 inches)
- Margins: Left 1.25 in (for binding), Right 1.0 in, Top 1.0 in, Bottom 1.0 in
- Font: Times New Roman
- Body: 12 pt, 1.15 line spacing, 6 pt after, justified
- Heading 1: 16 pt bold, Deep Navy (#1B365D), centered/left, page break before
- Heading 2: 13 pt bold, Deep Navy (#1B365D), 12 pt before, 4 pt after
- Heading 3: 11.5 pt bold, Dark Slate (#2C3E50), 8 pt before, 2 pt after
- Captions: 10 pt italic, centered
- Tables: Professional academic styling with navy headers, zebra rows, clean borders
"""

import os
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

NAVY_HEX = "1B365D"
SLATE_HEX = "2C3E50"
GRAY_BG_HEX = "F4F6F9"
BORDER_GRAY_HEX = "D0D5DD"
WHITE_HEX = "FFFFFF"

COLOR_NAVY = RGBColor(27, 54, 93)
COLOR_SLATE = RGBColor(44, 62, 80)
COLOR_CHARCOAL = RGBColor(33, 37, 41)
COLOR_MUTED = RGBColor(108, 117, 125)


def setup_document_styles(doc):
    """Configures page geometry, margins, and core styles."""
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)   # 1.25 inch binding gutter
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

    # Base Normal style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = COLOR_CHARCOAL
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(6)
    style_normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def set_cell_shading(cell, color_hex):
    """Sets background fill color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    # Remove existing shading if present
    for child in list(tcPr):
        if child.tag.endswith('shd'):
            tcPr.remove(child)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_horizontal_borders(table, color="CCCCCC", sz="4"):
    """Applies clean horizontal-only academic table borders."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def set_callout_box_borders(table, color="1B365D", sz="24"):
    """Applies a thick left accent border and clears other borders for a callout card."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_chapter_heading(doc, chapter_num, title):
    """Adds a major Chapter header with page break and formal typography."""
    p_num = doc.add_paragraph()
    p_num.paragraph_format.page_break_before = True
    p_num.paragraph_format.space_before = Pt(24)
    p_num.paragraph_format.space_after = Pt(4)
    p_num.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_num = p_num.add_run(f"CHAPTER {chapter_num}")
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(14)
    r_num.font.bold = True
    r_num.font.color.rgb = COLOR_NAVY

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(20)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(title.upper())
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = COLOR_NAVY

    # Add hidden Heading 1 for Word TOC indexing
    p_hidden = doc.add_paragraph(f"{chapter_num}. {title}", style='Heading 1')
    p_hidden.paragraph_format.space_before = Pt(0)
    p_hidden.paragraph_format.space_after = Pt(0)
    # Hide the text of the hidden heading so it doesn't double print
    r_h = p_hidden.runs[0]
    r_h.font.size = Pt(1)
    r_h.font.color.rgb = RGBColor(255, 255, 255)
    r_h.element.rPr.append(parse_xml(f'<w:vanish {nsdecls("w")}/>'))

    return p_title


def add_front_matter_heading(doc, title):
    """Adds a major front matter section heading (e.g., ABSTRACT, ACKNOWLEDGEMENT)."""
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(18)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title.upper())
    r.font.name = 'Times New Roman'
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = COLOR_NAVY
    return p


def add_section_heading(doc, sec_num_str, title_text, level=2):
    """Adds a numbered section or subsection heading."""
    p = doc.add_paragraph()
    p.paragraph_format.keep_with_next = True
    if level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{sec_num_str}  {title_text}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = COLOR_NAVY
        # Also register heading style for outline
        p.style = doc.styles['Heading 2']
        # override formatting on run
        r.font.color.rgb = COLOR_NAVY
        r.font.size = Pt(13)
        r.font.name = 'Times New Roman'
    else:
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{sec_num_str}  {title_text}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = COLOR_SLATE
        p.style = doc.styles['Heading 3']
        r.font.color.rgb = COLOR_SLATE
        r.font.size = Pt(11.5)
        r.font.name = 'Times New Roman'
    return p


def add_body_paragraph(doc, text, bold_prefix=None, italic_prefix=None, space_after=6):
    """Adds a standard justified body paragraph with optional prefix."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)

    if bold_prefix:
        r_b = p.add_run(bold_prefix + " ")
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(12)
        r_b.font.bold = True
        r_b.font.color.rgb = COLOR_CHARCOAL

    if italic_prefix:
        r_i = p.add_run(italic_prefix + " ")
        r_i.font.name = 'Times New Roman'
        r_i.font.size = Pt(12)
        r_i.font.italic = True
        r_i.font.color.rgb = COLOR_CHARCOAL

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12)
    r_text.font.color.rgb = COLOR_CHARCOAL
    return p


def add_bullet_point(doc, text, bold_prefix=None):
    """Adds a formatted bullet point."""
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)

    if bold_prefix:
        r_b = p.add_run(bold_prefix + " ")
        r_b.font.name = 'Times New Roman'
        r_b.font.size = Pt(12)
        r_b.font.bold = True
        r_b.font.color.rgb = COLOR_CHARCOAL

    r_text = p.add_run(text)
    r_text.font.name = 'Times New Roman'
    r_text.font.size = Pt(12)
    r_text.font.color.rgb = COLOR_CHARCOAL
    return p


def add_callout_box(doc, text, title=None):
    """Adds a highlighted callout box for key algorithms, problem statements, or findings."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    cell = tbl.cell(0, 0)
    cell.width = Inches(6.0)
    set_cell_shading(cell, GRAY_BG_HEX)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    set_callout_box_borders(tbl, color=NAVY_HEX, sz="24")

    p = cell.paragraphs[0]
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)

    if title:
        r_t = p.add_run(f"★  {title}\n")
        r_t.font.name = 'Times New Roman'
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_NAVY

    r_body = p.add_run(text)
    r_body.font.name = 'Times New Roman'
    r_body.font.size = Pt(10.5)
    r_body.font.italic = True
    r_body.font.color.rgb = COLOR_CHARCOAL

    # Extra spacing after table
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(2)
    p_sp.paragraph_format.space_after = Pt(6)


def add_equation(doc, eq_text, eq_num):
    """Adds a cleanly formatted mathematical equation with right-aligned numbering."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Widths: left = 5.2 in, right = 0.8 in
    cell_eq = tbl.cell(0, 0)
    cell_num = tbl.cell(0, 1)
    cell_eq.width = Inches(5.2)
    cell_num.width = Inches(0.8)

    # Clear borders
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/><w:bottom w:val="none"/><w:left w:val="none"/><w:right w:val="none"/>'
        f'<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    p_eq = cell_eq.paragraphs[0]
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_eq.paragraph_format.space_after = Pt(2)
    r_eq = p_eq.add_run(eq_text)
    r_eq.font.name = 'Cambria Math'
    r_eq.font.size = Pt(11)
    r_eq.font.italic = True
    r_eq.font.color.rgb = COLOR_CHARCOAL

    p_num = cell_num.paragraphs[0]
    p_num.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_after = Pt(2)
    r_num = p_num.add_run(f"({eq_num})")
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(11)
    r_num.font.bold = True
    r_num.font.color.rgb = COLOR_SLATE

    p_post = doc.add_paragraph()
    p_post.paragraph_format.space_before = Pt(0)
    p_post.paragraph_format.space_after = Pt(4)


def add_styled_table(doc, headers, data, col_widths=None, caption=None, table_num=None):
    """
    Renders an academic table with dark navy header, zebra-striped data rows,
    subtle horizontal rules, and centered table caption.
    """
    if caption and table_num:
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(10)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.keep_with_next = True
        r_num = p_cap.add_run(f"Table {table_num}: ")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(10.5)
        r_num.font.bold = True
        r_num.font.color.rgb = COLOR_NAVY
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(10.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = COLOR_CHARCOAL

    num_rows = len(data) + 1
    num_cols = len(headers)
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    set_table_horizontal_borders(tbl, color="B0BEC5", sz="6")

    # Header Row
    hdr_row = tbl.rows[0]
    # Set header row repeat on every page
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for col_idx, header_text in enumerate(headers):
        cell = hdr_row.cells[col_idx]
        set_cell_shading(cell, NAVY_HEX)
        set_cell_margins(cell, top=140, bottom=140, left=120, right=120)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(header_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for row_idx, row_values in enumerate(data):
        row = tbl.rows[row_idx + 1]
        bg_color = GRAY_BG_HEX if (row_idx % 2 == 1) else WHITE_HEX
        for col_idx, val in enumerate(row_values):
            cell = row.cells[col_idx]
            set_cell_shading(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05

            # Align left for text, center for numbers/short codes
            val_str = str(val).strip()
            if col_idx == 0 and not val_str.replace('.', '').isdigit():
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            elif any(c.isalpha() for c in val_str) and len(val_str) > 15:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = p.add_run(val_str)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(9.5)
            run.font.color.rgb = COLOR_CHARCOAL

    # Set column widths if provided
    if col_widths and len(col_widths) == num_cols:
        for r in tbl.rows:
            for c_idx, w in enumerate(col_widths):
                r.cells[c_idx].width = Inches(w)

    p_post = doc.add_paragraph()
    p_post.paragraph_format.space_before = Pt(4)
    p_post.paragraph_format.space_after = Pt(8)
    return tbl


def add_figure(doc, img_path, caption, fig_num, width_inches=5.8):
    """Embeds an image centered with a bold academic caption below it."""
    if not os.path.exists(img_path):
        p_err = doc.add_paragraph(f"[Image missing: {img_path}]")
        p_err.alignment = WD_ALIGN_PARAGRAPH.CENTER
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(10)
    p_img.paragraph_format.space_after = Pt(4)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(12)
    r_num = p_cap.add_run(f"Figure {fig_num}: ")
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(10)
    r_num.font.bold = True
    r_num.font.color.rgb = COLOR_NAVY

    r_cap = p_cap.add_run(caption)
    r_cap.font.name = 'Times New Roman'
    r_cap.font.size = Pt(10)
    r_cap.font.italic = True
    r_cap.font.color.rgb = COLOR_CHARCOAL
    return p_cap
