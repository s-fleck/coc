# Call of Cthulhu PDF Cheat Sheets

Generates professional PDF cheat sheets for Call of Cthulhu RPG from YAML configurations.

## Features

- **Unicode & Emoji Support**: Full support for Unicode characters and emojis 🎲
- **Configurable Colors**: Customize all colors via `config.yml`
- **Professional Layout**: Icon-based cards with alternating backgrounds
- **Markdown Support**: Rich text formatting in descriptions
- **Multiple Cheat Sheets**: Support for multiple YAML files

## Quick Start

1. **Install dependencies**:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt  # If you have one, or install manually
   ```

2. **Generate PDFs**:
   ```bash
   python build_pdf.py
   ```

## Font Setup (Optional)

For full emoji support 🎲⚔️🛡️, add Unicode fonts to the `fonts/` directory:

```bash
cd fonts
python download_fonts.py  # Check current font status
```

**Recommended**: Download [Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans) fonts for best emoji support.

## File Structure

```
├── build_pdf.py          # Main PDF generator
├── config.yml            # Color configuration
├── fonts/                # Embedded fonts directory
│   └── README.md         # Font installation guide
└── rules/                # YAML cheat sheet definitions
    ├── firearms.yml
    ├── evasion.yml
    ├── movement.yml
    └── meele-and-throw.yml
```
