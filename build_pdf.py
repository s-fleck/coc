import yaml
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import os
import glob
import markdown
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Line
from reportlab.lib.utils import ImageReader
from PIL import Image
import os

class IconPlaceholder(Flowable):
    """Display an actual icon image or placeholder"""
    def __init__(self, icon_path, width=20*mm, height=20*mm):
        self.icon_path = icon_path
        self.width = width
        self.height = height
    
    def draw(self):
        # Check if the icon file exists
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                # Load and draw the actual image
                img = ImageReader(self.icon_path)
                self.canv.drawImage(img, 0, 0, self.width, self.height, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                # Fall back to placeholder if image loading fails
                self._draw_placeholder()
        else:
            # Draw placeholder if no image or file doesn't exist
            self._draw_placeholder()
    
    def _draw_placeholder(self):
        """Draw a simple rectangular placeholder"""
        self.canv.setStrokeColor(colors.black)
        self.canv.setFillColor(colors.lightgrey)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        # Add icon text
        self.canv.setFillColor(colors.black)
        self.canv.setFont("Helvetica", 8)
        # Center the text in the rectangle
        text_width = self.canv.stringWidth("ICON", "Helvetica", 8)
        x = (self.width - text_width) / 2
        y = self.height / 2 - 2
        self.canv.drawString(x, y, "ICON")

class LineSeparator(Flowable):
    """A simple line separator in muted gray"""
    def __init__(self, width, height=1):
        self.width = width
        self.height = height
    
    def draw(self):
        self.canv.setStrokeColor(colors.lightgrey)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, self.height/2, self.width, self.height/2)

def markdown_to_paragraphs(md_text, style):
    """Convert markdown text to reportlab paragraphs"""
    if not md_text:
        return []
    
    # Convert markdown to HTML
    html = markdown.markdown(md_text.strip())
    
    # Simple conversion - just handle basic formatting
    # Remove HTML tags for now and return as paragraph
    import re
    text = re.sub('<[^<]+?>', '', html)
    text = text.replace('&gt;', '>').replace('&lt;', '<')
    
    return [Paragraph(text, style)]

# ---------- Process YAML Files ----------
def process_yaml_file(yaml_path):
    # Extract base filename (without extension) for the PDF output
    base_name = os.path.basename(yaml_path)
    pdf_name = os.path.splitext(base_name)[0] + ".pdf"

    print(f"Processing: {yaml_path} → {pdf_name}")

    # Load YAML data
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    # ---------- PDF Setup ----------
    styles = getSampleStyleSheet()
    
    # Create custom styles - optimized for compact, readable B&W printing
    page_header_style = ParagraphStyle(
        'PageHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=12,
        textColor=colors.black,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    card_header_style = ParagraphStyle(
        'CardHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=0,
        spaceAfter=3,
        textColor=colors.black,
        leftIndent=0,
        fontName='Helvetica-Bold'
    )
    
    # Style for skill text in header (smaller font)
    skill_header_style = ParagraphStyle(
        'SkillHeader',
        parent=styles['Normal'],
        fontSize=8,
        spaceBefore=0,
        spaceAfter=0,
        textColor=colors.black,
        leftIndent=0,
        fontName='Helvetica-Oblique'
    )
    
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Helvetica'
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )

    doc = SimpleDocTemplate(pdf_name, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    # ---------- Build Info Cards ----------
    for section, content in data.items():
        # Page header (top level key)
        elements.append(Paragraph(section.replace("_", " ").title(), page_header_style))
        elements.append(Spacer(1, 6*mm))

        # Process each subsection (actions, modifiers, etc.)
        for subsection_name, subsection_content in content.items():
            if subsection_name.lower() == "modifiers":
                # Process as mini cards in a 4-column grid - compact layout
                elements.append(Spacer(1, 3*mm))
                elements.append(Paragraph("Modifiers", card_header_style))
                elements.append(Spacer(1, 2*mm))
                
                # Create mini card style - optimized for B&W printing
                mini_card_style = ParagraphStyle(
                    'MiniCard',
                    parent=styles['Normal'],
                    fontSize=7,
                    alignment=TA_CENTER,
                    spaceAfter=2,
                    fontName='Helvetica'
                )
                
                # Convert subsection content to list for processing
                mini_cards = list(subsection_content.items())
                
                # Process mini cards in rows of 4
                for i in range(0, len(mini_cards), 4):
                    row_cards = mini_cards[i:i+4]
                    mini_card_data = []
                    
                    # Create the row with up to 4 mini cards
                    card_cells = []
                    for action_key, props in row_cards:
                        # Create mini card content with heading
                        icon_path = props.get("icon", "")
                        mini_icon = IconPlaceholder(icon_path, width=15*mm, height=15*mm)
                        
                        # Add heading for the mini card
                        heading_text = action_key.replace("_", " ").title()
                        heading_para = Paragraph(f"<b>{heading_text}</b>", mini_card_style)
                        
                        # Create content elements list
                        card_content = [mini_icon, Spacer(1, 1*mm), heading_para]
                        
                        # Add description if present
                        description_text = props.get("description", "")
                        if description_text:
                            desc_para = Paragraph(description_text, mini_card_style)
                            card_content.extend([Spacer(1, 1*mm), desc_para])
                        
                        # Add positive effect if present (red/bold for color, bold for B&W)
                        positive_text = props.get("positive", "")
                        if positive_text:
                            positive_para = Paragraph(f'<b>[+] {positive_text}</b>', mini_card_style)
                            card_content.extend([Spacer(1, 1*mm), positive_para])
                        
                        # Add negative effect if present (green/italic for color, italic for B&W) 
                        negative_text = props.get("negative", "")
                        if negative_text:
                            negative_para = Paragraph(f'<i>[-] {negative_text}</i>', mini_card_style)
                            card_content.extend([Spacer(1, 1*mm), negative_para])
                        
                        # Stack all content vertically
                        card_cells.append(card_content)
                    
                    # Fill empty cells if less than 4 cards in the row
                    while len(card_cells) < 4:
                        card_cells.append("")
                    
                    mini_card_data.append(card_cells)
                    
                    # Create table for this row of mini cards - B&W optimized
                    mini_table = Table(mini_card_data)
                    mini_table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 3),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                    ]))
                    
                    # Keep each row of mini cards together
                    elements.append(KeepTogether([mini_table, Spacer(1, 2*mm)]))
            
            elif subsection_name.lower() in ["actions", "rules"]:
                # Process as regular cards (actions, rules, etc.)
                for action_key, props in subsection_content.items():
                    # Create a regular card for each action
                    card_elements = []
                    
                    # Create icon placeholder
                    icon_path = props.get("icon", "")
                    icon = IconPlaceholder(icon_path)
                    
                    # Description as markdown
                    description_text = props.get("description", "")
                    description_paragraphs = markdown_to_paragraphs(description_text, description_style)
                    
                    # Create cost/gain table data
                    table_data = []
                    
                    # Add cost if present
                    if props.get("cost"):
                        table_data.append(["Cost:", props.get("cost")])
                    
                    # Add gain if present  
                    if props.get("gain"):
                        table_data.append(["Gain:", props.get("gain")])
                        
                    # Add effect if present
                    if props.get("effect"):
                        table_data.append(["Effect:", props.get("effect")])
                    
                    # Build the card content - compact layout with heading and description next to icon
                    card_elements = []
                    
                    # Create content to go next to the icon (heading + description)
                    content_elements = []
                    
                    # Add the header (with skill if present)
                    header_title = action_key.replace("_", " ").title()
                    skill_text = props.get("skill", "")
                    
                    if skill_text:
                        # Create a table with title on left and skill on right
                        # Calculate width to match the available content width
                        # Available width = page width - margins - icon width - paddings
                        available_width = (A4[0] - 40*mm - 20*mm - 5*mm - 8*mm)  # page - margins - icon - left/right padding
                        header_data = [[
                            Paragraph(f"<b>{header_title}</b>", card_header_style),
                            Paragraph(f"<i>{skill_text}</i>", skill_header_style)
                        ]]
                        header_table = Table(header_data, colWidths=[available_width * 0.6, available_width * 0.4])
                        header_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'LEFT'),     # Title left-aligned
                            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),    # Skill right-aligned
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        content_elements.append(header_table)
                    else:
                        # Simple header without skill
                        content_elements.append(Paragraph(f"<b>{header_title}</b>", card_header_style))
                    
                    # Add description paragraphs
                    for para in description_paragraphs:
                        content_elements.append(para)
                    
                    # Create a table with icon on left and all content (header + description) on right
                    if content_elements:
                        # Combine all content into a single cell content
                        content_data = [[icon, content_elements]]
                        
                        content_table = Table(content_data, colWidths=[20*mm, None])
                        content_table.setStyle(TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (0, -1), 0),  # Icon column - no left padding
                            ('LEFTPADDING', (1, 0), (-1, -1), 5),  # Content column - add left padding
                            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                            ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ]))
                        
                        card_elements.append(content_table)
                    else:
                        # Just icon if no content
                        icon_table = Table([[icon]], colWidths=[20*mm])
                        icon_table.setStyle(TableStyle([
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ]))
                        card_elements.append(icon_table)
                    
                    # Add cost/gain table if there's data - optimized for B&W printing
                    if table_data:
                        # Convert table data to paragraphs
                        table_data_formatted = []
                        for row in table_data:
                            table_data_formatted.append([
                                Paragraph(f"<b>{row[0]}</b>", table_cell_style),
                                Paragraph(str(row[1]), table_cell_style)
                            ])
                        
                        info_table = Table(table_data_formatted, colWidths=[25*mm, None])
                        info_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                            ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                            ('LEFTPADDING', (0, 0), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                        ]))
                        
                        card_elements.append(Spacer(1, 2*mm))
                        card_elements.append(info_table)
                    
                    # Add each card element directly to the main flow
                    # Wrap the entire card including separator in KeepTogether to prevent page breaks
                    card_with_separator = [LineSeparator(180*mm, 1*mm)]
                    card_with_separator.extend(card_elements)
                    card_with_separator.append(Spacer(1, 3*mm))
                    
                    elements.append(KeepTogether(card_with_separator))

        # Add page break between sections
        if section != list(data.keys())[-1]:  # Don't add page break after last section
            elements.append(PageBreak())

    # Build the PDF
    doc.build(elements)
    print(f"✅ PDF created: {pdf_name}")

# ---------- Main Execution ----------
if __name__ == "__main__":
    # Create rules directory if it doesn't exist
    if not os.path.exists("rules"):
        os.makedirs("rules")
        print("Created 'rules' directory. Please add your YAML files there.")

    # Get all YAML files from the rules directory
    yaml_files = glob.glob(os.path.join("rules", "*.yaml"))
    yaml_files.extend(glob.glob(os.path.join("rules", "*.yml")))

    if not yaml_files:
        print("No YAML files found in the 'rules' folder. Please add some files.")
    else:
        print(f"Found {len(yaml_files)} YAML file(s) to process.")
        for yaml_file in yaml_files:
            process_yaml_file(yaml_file)