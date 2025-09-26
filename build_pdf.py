import yaml
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import glob
import markdown
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Line
from reportlab.lib.utils import ImageReader
from PIL import Image
import os

# Register Unicode-compatible font for emoji support
def register_unicode_fonts():
    """Register Unicode-compatible fonts that support emojis from embedded font files"""
    import os
    import zipfile
    
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    
    # Auto-extract Noto fonts from zip if available and fonts not already extracted
    noto_zip = os.path.join(fonts_dir, 'Noto_Sans.zip')
    if os.path.exists(noto_zip):
        noto_files = ['NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', 'NotoSans-Italic.ttf']
        if not all(os.path.exists(os.path.join(fonts_dir, f)) for f in noto_files[:3]):  # Check first 3
            try:
                with zipfile.ZipFile(noto_zip, 'r') as zip_ref:
                    all_files = zip_ref.namelist()
                    
                    # Map target names to possible paths in zip
                    font_mapping = {
                        'NotoSans-Regular.ttf': ['static/NotoSans-Regular.ttf', 'NotoSans-Regular.ttf'],
                        'NotoSans-Bold.ttf': ['static/NotoSans-Bold.ttf', 'NotoSans-Bold.ttf'],
                        'NotoSans-Italic.ttf': ['static/NotoSans-Italic.ttf', 'NotoSans-Italic.ttf'],
                        'NotoSans-BoldItalic.ttf': ['static/NotoSans-BoldItalic.ttf', 'NotoSans-BoldItalic.ttf']
                    }
                    
                    extracted = 0
                    for target_name, possible_paths in font_mapping.items():
                        target_file = os.path.join(fonts_dir, target_name)
                        if os.path.exists(target_file):
                            continue  # Already exists
                            
                        for possible_path in possible_paths:
                            if possible_path in all_files:
                                zip_ref.extract(possible_path, fonts_dir)
                                extracted_path = os.path.join(fonts_dir, possible_path)
                                if extracted_path != target_file:
                                    os.rename(extracted_path, target_file)
                                extracted += 1
                                break
                    
                    # Clean up extracted subdirectories
                    for subdir in ['static', 'Noto_Sans']:
                        subdir_path = os.path.join(fonts_dir, subdir)
                        if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                            try:
                                os.rmdir(subdir_path)
                            except OSError:
                                pass
                    
                    if extracted > 0:
                        print(f"📦 Auto-extracted {extracted} Noto Sans fonts from zip")
                        
            except Exception as e:
                print(f"Warning: Could not extract fonts from zip: {e}")
    
    # Register Noto Emoji font for emoji support (but not as primary font)
    emoji_registered = False
    noto_emoji_variable = os.path.join(fonts_dir, 'NotoEmoji-VariableFont_wght.ttf')
    if os.path.exists(noto_emoji_variable):
        try:
            pdfmetrics.registerFont(TTFont('NotoEmoji', noto_emoji_variable))
            print("🎉 Registered Noto Emoji Variable Font for emoji support")
            emoji_registered = True
        except Exception as e:
            print(f"Warning: Could not register Noto Emoji font: {e}")
    
    # Try to register Windows emoji font as additional fallback
    if not emoji_registered:
        try:
            import platform
            if platform.system() == "Windows":
                emoji_fonts = [
                    ('C:/Windows/Fonts/seguiemj.ttf', 'SegoeEmoji'),
                    ('C:/Windows/Fonts/NotoColorEmoji.ttf', 'NotoColorEmoji'),
                ]
                
                for font_path, font_name in emoji_fonts:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        print(f"✅ Registered {font_name} for emoji support")
                        emoji_registered = True
                        break
        except Exception as e:
            print(f"Warning: Could not register system emoji font: {e}")
    
    try:
        # Try to register Noto Sans fonts as PRIMARY font (for regular text)
        noto_regular = os.path.join(fonts_dir, 'NotoSans-Regular.ttf')
        noto_bold = os.path.join(fonts_dir, 'NotoSans-Bold.ttf')
        noto_italic = os.path.join(fonts_dir, 'NotoSans-Italic.ttf')
        noto_bold_italic = os.path.join(fonts_dir, 'NotoSans-BoldItalic.ttf')
        
        if all(os.path.exists(f) for f in [noto_regular, noto_bold, noto_italic]):
            pdfmetrics.registerFont(TTFont('NotoSans', noto_regular))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', noto_bold))
            pdfmetrics.registerFont(TTFont('NotoSans-Italic', noto_italic))
            if os.path.exists(noto_bold_italic):
                pdfmetrics.registerFont(TTFont('NotoSans-BoldItalic', noto_bold_italic))
            else:
                pdfmetrics.registerFont(TTFont('NotoSans-BoldItalic', noto_bold))  # fallback
            
            # Register the font family
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily('NotoSans',normal='NotoSans',bold='NotoSans-Bold',italic='NotoSans-Italic',boldItalic='NotoSans-BoldItalic')
            
            emoji_status = "with full emoji support" if emoji_registered else "(limited emoji - add NotoEmoji-VariableFont_wght.ttf for emoji support)"
            print(f"✅ Using Noto Sans fonts for text {emoji_status}")
            return 'NotoSans'
            
    except Exception as e:
        print(f"Warning: Could not load Noto Sans fonts: {e}")
    
    try:
        # Fallback: Try Windows system fonts with emoji font
        import platform
        if platform.system() == "Windows":
            pdfmetrics.registerFont(TTFont('SegoeUI', 'C:/Windows/Fonts/segoeui.ttf'))
            pdfmetrics.registerFont(TTFont('SegoeUI-Bold', 'C:/Windows/Fonts/segoeuib.ttf'))
            pdfmetrics.registerFont(TTFont('SegoeUI-Italic', 'C:/Windows/Fonts/segoeuii.ttf'))
            
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily('SegoeUI',normal='SegoeUI',bold='SegoeUI-Bold',italic='SegoeUI-Italic',boldItalic='SegoeUI-Bold')
            
            emoji_status = "with emoji support" if emoji_registered else "(limited emoji support)"
            print(f"ℹ️ Using system Segoe UI fonts {emoji_status}")
            return 'SegoeUI'
    except:
        pass
    
    # Final fallback: Helvetica
    print("⚠️ Using Helvetica font (no emoji support). Add Noto fonts to fonts/ directory for full Unicode/emoji support.")
    return 'Helvetica'

# Initialize Unicode font
UNICODE_FONT = register_unicode_fonts()
UNICODE_FONT_BOLD = UNICODE_FONT + '-Bold' if UNICODE_FONT != 'Helvetica' else 'Helvetica-Bold'
UNICODE_FONT_OBLIQUE = (UNICODE_FONT + '-Italic' if UNICODE_FONT in ['NotoSans', 'SegoeUI'] 
                       else (UNICODE_FONT + '-Oblique' if UNICODE_FONT == 'DejaVuSans' 
                            else 'Helvetica-Oblique'))

def load_color_config():
    """Load color configuration from config.yml"""
    try:
        with open('config.yml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            color_dict = {}
            for name, rgb in config['colors'].items():
                color_dict[name] = colors.Color(rgb['r'], rgb['g'], rgb['b'])
            return color_dict
    except FileNotFoundError:
        print("Warning: config.yml not found. Using default colors.")
        return {
            'card_background_1': colors.Color(0.95, 0.95, 0.95),
            'card_background_2': colors.white,
            'page_header_text': colors.black,
            'card_header_text': colors.black,
            'skill_header_text': colors.Color(0.4, 0.4, 0.4),
            'description_text': colors.Color(0.2, 0.2, 0.2),
            'table_cell_text': colors.Color(0.1, 0.1, 0.1),
            'page_header_background': colors.white,
            'modifier_background': colors.Color(0.9, 0.9, 0.9),
            'modifier_spacing': colors.white,
            'positive_effect': colors.Color(0.0, 0.6, 0.0),
            'negative_effect': colors.Color(0.8, 0.0, 0.0),
            'icon_background': colors.Color(0.85, 0.85, 0.85),
            'icon_border': colors.black,
            'separator_line': colors.Color(0.7, 0.7, 0.7)
        }

class IconPlaceholder(Flowable):
    """Display an actual icon image or placeholder"""
    def __init__(self, icon_path, width=20*mm, height=20*mm, colors_config=None):
        self.icon_path = icon_path
        self.width = width
        self.height = height
        self.colors_config = colors_config or {}
    
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
        icon_border = self.colors_config.get('icon_border', colors.black)
        icon_bg = self.colors_config.get('icon_background', colors.lightgrey)
        
        self.canv.setStrokeColor(icon_border)
        self.canv.setFillColor(icon_bg)
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=1)
        # Add icon text
        self.canv.setFillColor(icon_border)
        self.canv.setFont("Helvetica", 8)
        # Center the text in the rectangle
        text_width = self.canv.stringWidth("ICON", "Helvetica", 8)
        x = (self.width - text_width) / 2
        y = self.height / 2 - 2
        self.canv.drawString(x, y, "ICON")

class LineSeparator(Flowable):
    """A simple line separator in configurable color"""
    def __init__(self, width, height=1, colors_config=None):
        self.width = width
        self.height = height
        self.colors_config = colors_config or {}
    
    def draw(self):
        separator_color = self.colors_config.get('separator_line', colors.lightgrey)
        self.canv.setStrokeColor(separator_color)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, self.height/2, self.width, self.height/2)

def process_emojis_in_text(text):
    """Process text to wrap emojis in font tags for proper rendering"""
    import re
    
    # Check if emoji font is available
    emoji_font = None
    try:
        from reportlab.pdfbase.pdfmetrics import getFont
        if 'NotoEmoji' in [f.fontName for f in pdfmetrics._fonts.values()]:
            emoji_font = 'NotoEmoji'
        elif 'SegoeEmoji' in [f.fontName for f in pdfmetrics._fonts.values()]:
            emoji_font = 'SegoeEmoji'
        elif 'NotoColorEmoji' in [f.fontName for f in pdfmetrics._fonts.values()]:
            emoji_font = 'NotoColorEmoji'
    except:
        pass
    
    if not emoji_font:
        return text  # No emoji font available, return as-is
    
    # Regex pattern to match emoji characters
    # This covers most common emoji ranges
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U0001F200-\U0001F2FF\U0001F000-\U0001F0FF\U00002700-\U000027BF\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U00002B00-\U00002BFF]+'
    
    def replace_emoji(match):
        emoji = match.group(0)
        return f'<font name="{emoji_font}">{emoji}</font>'
    
    return re.sub(emoji_pattern, replace_emoji, text)

def markdown_to_paragraphs(md_text, style):
    """Convert markdown text to reportlab paragraphs with emoji support"""
    if not md_text:
        return []
    
    # First process emojis
    md_text = process_emojis_in_text(md_text)
    
    # First, handle double newlines in the raw text before markdown processing
    # This is important for literal block scalars (|) in YAML
    import re
    
    # Normalize line endings and handle paragraph breaks
    normalized_text = md_text.strip()
    # Convert double newlines (paragraph breaks) to a special marker
    paragraph_marker = "|||PARAGRAPH_BREAK|||"
    normalized_text = re.sub(r'\n\s*\n', f'\n\n{paragraph_marker}\n\n', normalized_text)
    
    # Convert markdown to HTML
    html = markdown.markdown(normalized_text)
    
    # Convert HTML to ReportLab compatible format
    text = html
    text = re.sub(r'<p>(.*?)</p>', r'\1<br/>', text)  # Convert HTML paragraphs
    text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text)  # Italic
    
    # Handle inline code formatting (backticks in markdown)
    # Convert <code> tags to a styled format that looks like code
    text = re.sub(r'<code>(.*?)</code>', r'<font name="Courier"><b>\1</b></font>', text)  # Code style
    
    # Handle bullet points (HTML lists)
    text = re.sub(r'<ul>', '', text)  # Remove ul tags
    text = re.sub(r'</ul>', '<br/>', text)  # Replace closing ul with line break
    text = re.sub(r'<li>(.*?)</li>', r'• \1<br/>', text)  # Convert li to bullet points
    
    # Convert our paragraph break markers to actual breaks
    text = text.replace(paragraph_marker, '<br/><br/>')
    # Also handle the marker wrapped in HTML paragraphs
    text = re.sub(rf'<p>{re.escape(paragraph_marker)}</p>', '<br/><br/>', text)
    
    # Handle manual line breaks from HTML <br> tags (if any exist)
    text = re.sub(r'<br\s*/?>', '<br/>', text)  # Normalize br tags
    
    # Clean up extra line breaks and HTML entities
    text = re.sub(r'<br/><br/><br/>', '<br/><br/>', text)  # Remove triple breaks
    text = re.sub(r'<br/><br/>$', '', text)  # Remove trailing double breaks
    text = re.sub(r'<br/>$', '', text)  # Remove single trailing break
    text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
    
    # Split on double line breaks for multiple paragraphs
    paragraphs = []
    parts = text.split('<br/><br/>')
    for part in parts:
        if part.strip():
            paragraphs.append(Paragraph(part.strip(), style))
    
    return paragraphs if paragraphs else [Paragraph(text, style)]

def markdown_to_text(md_text):
    """Convert markdown text to reportlab-compatible text (for single line properties) with emoji support"""
    if not md_text:
        return ""
    
    # First process emojis
    md_text = process_emojis_in_text(md_text)
    
    # Convert markdown to HTML
    html = markdown.markdown(str(md_text).strip())
    
    import re
    # Convert HTML to ReportLab compatible format
    text = html
    # Remove paragraph tags for single-line content
    text = re.sub(r'<p>(.*?)</p>', r'\1', text)
    text = re.sub(r'<strong>(.*?)</strong>', r'<b>\1</b>', text)  # Bold
    text = re.sub(r'<em>(.*?)</em>', r'<i>\1</i>', text)  # Italic
    text = re.sub(r'<code>(.*?)</code>', r'<font name="Courier"><b>\1</b></font>', text)  # Code
    
    # Clean up HTML entities
    text = text.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
    
    return text

# ---------- Process YAML Files ----------
def process_yaml_file(yaml_path):
    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract base filename (without extension) for the PDF output
    base_name = os.path.basename(yaml_path)
    pdf_name = os.path.join(output_dir, os.path.splitext(base_name)[0] + ".pdf")

    print(f"Processing: {yaml_path} → {pdf_name}")

    # Load YAML data
    with open(yaml_path, "r", encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Load color configuration
    colors_config = load_color_config()

    # ---------- PDF Setup ----------
    styles = getSampleStyleSheet()
    
    # Create custom styles using configurable colors
    page_header_style = ParagraphStyle(
        'PageHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=12,
        textColor=colors_config['page_header_text'],
        backColor=colors_config['page_header_background'],
        alignment=TA_CENTER,
    )
    
    card_header_style = ParagraphStyle(
        'CardHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=0,
        spaceAfter=3,
        textColor=colors_config['card_header_text'],
        leftIndent=0,
        fontName=UNICODE_FONT_BOLD
    )
    
    # Enhanced style for modifiers section header
    modifiers_header_style = ParagraphStyle(
        'ModifiersHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=12,
        textColor=colors_config['page_header_text'],
        backColor=colors_config['page_header_background'],
        alignment=TA_CENTER,
    )
    
    # Style for skill text in header
    skill_header_style = ParagraphStyle(
        'SkillHeader',
        parent=styles['Normal'],
        fontSize=8,
        spaceBefore=0,
        spaceAfter=0,
        textColor=colors_config['skill_header_text'],
        leftIndent=0,
        fontName=UNICODE_FONT_OBLIQUE
    )
    
    description_style = ParagraphStyle(
        'Description',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName=UNICODE_FONT,
        textColor=colors_config['description_text']
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        fontName=UNICODE_FONT,
        textColor=colors_config['table_cell_text']
    )
    
    cost_gain_style = ParagraphStyle(
        'CostGain',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_LEFT,
        fontName=UNICODE_FONT,
        textColor=colors_config['table_cell_text']
    )

    doc = SimpleDocTemplate(pdf_name, pagesize=A4, topMargin=10*mm, bottomMargin=10*mm) # leftMargin=10*mm, rightMargin=10*mm
    elements = []

    # ---------- Build Info Cards ----------
    # Handle new flexible sheet structure
    if 'sheet' in data and 'sections' in data['sheet']:
        # New flexible structure: sheet -> sections -> items
        sections = data['sheet']['sections']
        
        for section in sections:
            # Handle two possible section structures:
            # 1. Direct: {title: "...", type: "...", items: [...]}
            # 2. Nested: {section_name: {title: "...", type: "...", items: [...]}}
            
            if 'title' in section and 'items' in section:
                # Direct structure
                section_title = section.get('title', 'Untitled Section')
                section_type = section.get('type', 'full_card')
                section_items = section.get('items', [])
            else:
                # Nested structure - find the first key that contains the section data
                section_key = next(iter(section.keys()))
                section_data = section[section_key]
                section_title = section_data.get('title', section_key.replace('_', ' ').title())
                section_type = section_data.get('type', 'full_card')
                section_items = section_data.get('items', [])
            
            # Add section header
            elements.append(Paragraph(section_title, page_header_style))
            elements.append(Spacer(1, 6*mm))
            
            if section_type == "mini_card":
                # Process as mini cards in a 4-column grid - compact layout
                elements.append(Spacer(1, 3*mm))
                
                # Create mini card style - optimized for B&W printing
                mini_card_style = ParagraphStyle(
                    'MiniCard',
                    parent=styles['Normal'],
                    fontSize=7,
                    alignment=TA_CENTER,
                    spaceAfter=2,
                    fontName=UNICODE_FONT
                )

                mini_card_header_style = ParagraphStyle(
                    'MiniCardHeader',
                    parent=styles['Normal'],
                    fontSize=12,
                    alignment=TA_CENTER,
                    spaceAfter=2,
                    fontName=UNICODE_FONT
                )
                
                # Create colored styles for positive/negative effects
                positive_style = ParagraphStyle(
                    'PositiveEffect',
                    parent=mini_card_style,
                    textColor=colors_config['positive_effect'],
                    fontName=UNICODE_FONT_BOLD
                )
                
                negative_style = ParagraphStyle(
                    'NegativeEffect', 
                    parent=mini_card_style,
                    textColor=colors_config['negative_effect'],
                    fontName=UNICODE_FONT_BOLD
                )
                
                # Skip if no items
                if not section_items:
                    continue
                
                # Process mini cards in rows of 4
                for i in range(0, len(section_items), 4):
                    row_cards = section_items[i:i+4]
                    mini_card_data = []
                    
                    # Create the row with up to 4 mini cards
                    card_cells = []
                    for item in row_cards:
                        # Create mini card content with heading
                        icon_path = item.get("icon", "")
                        mini_icon = IconPlaceholder(icon_path, width=15*mm, height=15*mm, colors_config=colors_config)
                        
                        # Add heading for the mini card
                        heading_text = item.get('title', 'Untitled')
                        heading_para = Paragraph(f"<b>{heading_text}</b>", mini_card_header_style)
                        
                        # Create content elements list
                        card_content = [mini_icon, Spacer(1, 1*mm), heading_para]
                        
                        # Add description if present
                        description_text = item.get('description', '')
                        if description_text:
                            description_formatted = process_emojis_in_text(markdown_to_text(description_text))
                            description_para = Paragraph(description_formatted, mini_card_style)
                            card_content.append(description_para)
                        
                        # Add positive effect if present
                        positive_text = item.get('positive', '')
                        if positive_text:
                            positive_formatted = process_emojis_in_text(markdown_to_text(positive_text))
                            positive_para = Paragraph(f"✓ {positive_formatted}", positive_style)
                            card_content.append(positive_para)
                        
                        # Add negative effect if present
                        negative_text = item.get('negative', '')
                        if negative_text:
                            negative_formatted = process_emojis_in_text(markdown_to_text(negative_text))
                            negative_para = Paragraph(f"✗ {negative_formatted}", negative_style)
                            card_content.append(negative_para)
                        
                        # Add gain/cost info if present
                        gain_text = item.get('gain', '')
                        if gain_text:
                            gain_formatted = process_emojis_in_text(markdown_to_text(gain_text))
                            gain_para = Paragraph(f"↗ {gain_formatted}", positive_style)
                            card_content.append(gain_para)
                        
                        # Combine all content into a single cell
                        combined_content = []
                        for element in card_content:
                            combined_content.append(element)
                        card_cells.append(combined_content)
                    
                    # Fill remaining cells if row has less than 4 cards
                    while len(card_cells) < 4:
                        card_cells.append("")
                    
                    mini_card_data.append(card_cells)
                    
                    # Create table with mini cards
                    col_width = (A4[0] - 20*mm) / 4  # Adjust for margins
                    mini_table = Table(mini_card_data, colWidths=[col_width] * 4)
                    mini_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),   # Increased padding for spacing
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),  # Increased padding for spacing
                        ('TOPPADDING', (0, 0), (-1, -1), 8),    # Increased padding for spacing
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8), # Increased padding for spacing
                        # Removed GRID to eliminate borders between mini cards
                        ('BACKGROUND', (0, 0), (-1, -1), colors_config['card_background_1'])
                    ]))
                    
                    # Keep each row of mini cards together
                    elements.append(KeepTogether([mini_table, Spacer(1, 2*mm)]))
            
            elif section_type == "full_card":
                # Process as regular full cards
                card_counter = 0  # Counter for alternating backgrounds
                for item in section_items:
                    # Create a regular card for each item
                    card_elements = []
                    
                    # Create icon placeholder
                    icon_path = item.get("icon", "")
                    main_icon = IconPlaceholder(icon_path, width=20*mm, height=20*mm, colors_config=colors_config)
                    
                    # Get item properties
                    header_title = item.get('title', 'Untitled')
                    skill_text = item.get('skill', '')
                    
                    if skill_text:
                        # Create a table with title on left and skill on right
                        # Calculate width to match the available content width
                        # Available width = page width - margins - icon width - paddings
                        available_width = (A4[0] - 20*mm - 20*mm - 5*mm - 8*mm)  # page - margins - icon - left/right padding
                        skill_formatted = process_emojis_in_text(markdown_to_text(skill_text))
                        header_data = [[
                            Paragraph(f"<b>{header_title}</b>", card_header_style),
                            Paragraph(f"<i>{skill_formatted}</i>", skill_header_style)
                        ]]
                        header_table = Table(header_data, colWidths=[available_width * 0.6, available_width * 0.4])
                        header_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ]))
                        card_elements.append(header_table)
                    else:
                        # Simple header without skill
                        header_text = f"<b>{header_title}</b>"
                        header_para = Paragraph(header_text, card_header_style)
                        card_elements.append(header_para)
                    
                    card_elements.append(Spacer(1, 1*mm))
                    
                    # Add description
                    description_text = item.get('description', '')
                    if description_text:
                        description_formatted = process_emojis_in_text(description_text)
                        description_paras = markdown_to_paragraphs(description_formatted, description_style)
                        for para in description_paras:
                            card_elements.append(para)
                        card_elements.append(Spacer(1, 2*mm))
                    
                    # Add cost/gain table if either exists
                    cost_text = item.get('cost', '')
                    gain_text = item.get('gain', '')
                    positive_text = item.get('positive', '')
                    negative_text = item.get('negative', '')
                    
                    # Combine gain and positive into gain_display
                    gain_display = []
                    if gain_text:
                        gain_display.append(gain_text)
                    if positive_text:
                        gain_display.append(positive_text)
                    
                    # Combine cost and negative into cost_display  
                    cost_display = []
                    if cost_text:
                        cost_display.append(cost_text)
                    if negative_text:
                        cost_display.append(negative_text)
                    
                    if cost_display or gain_display:
                        table_data = []
                        
                        if cost_display and gain_display:
                            # Both cost and gain - create combined row
                            cost_combined = ' // '.join(cost_display)
                            gain_combined = ' // '.join(gain_display)
                            cost_formatted = process_emojis_in_text(markdown_to_text(cost_combined))
                            gain_formatted = process_emojis_in_text(markdown_to_text(gain_combined))
                            table_data.append([
                                Paragraph(f"<b>Cost:</b> {cost_formatted}", cost_gain_style),
                                Paragraph(f"<b>Gain:</b> {gain_formatted}", cost_gain_style)
                            ])
                        elif cost_display:
                            # Only cost
                            cost_combined = ' // '.join(cost_display)
                            cost_formatted = process_emojis_in_text(markdown_to_text(cost_combined))
                            table_data.append([
                                Paragraph(f"<b>Cost:</b> {cost_formatted}", cost_gain_style),
                                ""
                            ])
                        elif gain_display:
                            # Only gain
                            gain_combined = ' // '.join(gain_display)
                            gain_formatted = process_emojis_in_text(markdown_to_text(gain_combined))
                            table_data.append([
                                "",
                                Paragraph(f"<b>Gain:</b> {gain_formatted}", cost_gain_style)
                            ])
                        
                        # Calculate available width for cost/gain table
                        # Available width = page width - margins - icon width - paddings
                        available_width = A4[0] - 20*mm - 25*mm - 5*mm - 8*mm  # page - margins - icon - paddings
                        cost_gain_table = Table(table_data, colWidths=[available_width/2, available_width/2])
                        cost_gain_table.setStyle(TableStyle([
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
                            ('TOPPADDING', (0, 0), (-1, -1), 2),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),  # No left padding since it's inside the main card
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # No right padding since it's inside the main card
                        ]))
                        card_elements.append(cost_gain_table)
                    
                    # Create the main card table with icon on the left and content on the right
                    card_table_data = [[main_icon, card_elements]]
                    card_table = Table(card_table_data, colWidths=[25*mm, None])
                    
                    # Determine background color (alternating)
                    bg_color = colors_config['card_background_1'] if card_counter % 2 == 0 else colors_config['card_background_2']
                    
                    card_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Icon alignment
                        ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # Content alignment
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                        # Removed GRID to eliminate vertical lines between icon and content
                        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Icon column - no left padding
                        ('RIGHTPADDING', (0, 0), (0, -1), 5), # Icon column - small right padding
                        ('LEFTPADDING', (1, 0), (-1, -1), 5), # Content column - left padding
                        ('RIGHTPADDING', (1, 0), (-1, -1), 8), # Content column - right padding
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    elements.append(card_table)
                    elements.append(Spacer(1, 3*mm))
                    card_counter += 1
    
    else:
        # If no 'sheet' structure found, show error message
        elements.append(Paragraph("Error: YAML file must have 'sheet' structure with 'sections'", page_header_style))

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