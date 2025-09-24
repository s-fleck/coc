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

class IconPlaceholder(Flowable):
    """A simple placeholder for an icon"""
    def __init__(self, icon_name, width=20*mm, height=20*mm):
        self.icon_name = icon_name
        self.width = width
        self.height = height
    
    def draw(self):
        # Draw a simple rectangular placeholder for the icon
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
    
    # Create custom styles
    page_header_style = ParagraphStyle(
        'PageHeader',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    )
    
    card_header_style = ParagraphStyle(
        'CardHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=5,
        spaceAfter=8,
        textColor=colors.darkgreen,
        leftIndent=0
    )
    
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leftIndent=5*mm,
        rightIndent=5*mm
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT
    )

    doc = SimpleDocTemplate(pdf_name, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    # ---------- Build Info Cards ----------
    for section, content in data.items():
        # Page header (top level key)
        elements.append(Paragraph(section.replace("_", " ").title(), page_header_style))
        elements.append(Spacer(1, 10*mm))

        for action_key, props in content.items():
            # Create a card for each action
            card_elements = []
            
            # Create icon placeholder
            icon_name = props.get("icon", "")
            icon = IconPlaceholder(icon_name)
            
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
                
            # Add skill if present
            if props.get("skill"):
                table_data.append(["Skill:", props.get("skill")])
                
            # Add effect if present
            if props.get("effect"):
                table_data.append(["Effect:", props.get("effect")])
            
            # Build the card content with a simpler approach
            card_elements = []
            
            # Add the header
            card_elements.append(Paragraph(action_key.replace("_", " ").title(), card_header_style))
            
            # Create a simple layout with icon and description side by side
            if description_paragraphs:
                # Create a table with icon and description side by side
                icon_desc_data = [[icon, description_paragraphs[0]]]
                
                icon_desc_table = Table(icon_desc_data, colWidths=[25*mm, None])
                icon_desc_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                
                card_elements.append(icon_desc_table)
                
                # Add any additional description paragraphs
                for para in description_paragraphs[1:]:
                    card_elements.append(para)
            else:
                # Just icon if no description
                icon_table = Table([[icon]], colWidths=[25*mm])
                icon_table.setStyle(TableStyle([
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ]))
                card_elements.append(icon_table)
            
            # Add cost/gain table if there's data
            if table_data:
                # Convert table data to paragraphs
                table_data_formatted = []
                for row in table_data:
                    table_data_formatted.append([
                        Paragraph(f"<b>{row[0]}</b>", table_cell_style),
                        Paragraph(str(row[1]), table_cell_style)
                    ])
                
                info_table = Table(table_data_formatted, colWidths=[30*mm, None])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ]))
                
                card_elements.append(Spacer(1, 3*mm))
                card_elements.append(info_table)
            
            # Add each card element directly to the main flow instead of wrapping in another table
            # Add a simple border using a line or spacer
            elements.append(Paragraph("_" * 80, styles['Normal']))  # Simple line separator
            
            for element in card_elements:
                elements.append(element)
                
            elements.append(Spacer(1, 5*mm))

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