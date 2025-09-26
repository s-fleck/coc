# Call of Cthulhu PDF Cheat Sheets

Generates PDF cheat sheets for Call of Cthulhu RPG from YAML files,
but probably reusable for other purposes. Based on the visual cheat sheets by `/u/Uncle_Bones_` from this redit thread:
https://www.reddit.com/r/callofcthulhu/comments/1aq0v34/visualised_cheat_sheets_for_combat_mechanics_i/ . All icons
were created by `/u/Uncle_Bones_` and are used with permission.

## 📖 Download PDFs

Latest cheat sheets built from master branch are available for download at [https://s-fleck.github.io/coc/](https://s-fleck.github.io/coc/)

Available cheat sheets:

- **Movement** 🚶‍♂️ - Movement actions
- **Evasion** 🤸 - Dodge mechanics and defensive actions
- **Firearms** 🎯 - Ranged combat actions
- **Melee & Throw** ⚔️ - Close combat and throwing actions
- **Pulp Luck** ⚔️ - Extra luck rules for Pulp Cthulhu

## Features

- **Unicode & Emoji Support**: Full support for Unicode characters and emojis 🎲
- **Configurable Colors**: Customize all colors via `config.yml`
- **Markdown Support**: Rich text formatting in descriptions

## Development status

This is in a proof-of-concept state and the code is 100% AI generated without much human oversight.
That beeing said, it generates clean-looking printable cheat sheets and supports all envisioned features.
The cheat sheets will probably be refined and extended for Cthulhu Invictus and Pulp Cthulhu over the
course of 2025/2026 as I started this project specificaly to support a campaign that uses those rule sets.

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

## File Structure

```
├── .github/
│   └── workflows/
│       └── deploy-pdfs.yml   # GitHub Actions workflow
├── docs/
│   └── index.html           # GitHub Pages site
├── output/                  # Generated PDFs (local)
├── build_pdf.py            # Main PDF generator
├── config.yml              # Color configuration
├── fonts/                  # Embedded fonts directory
│   └── README.md           # Font installation guide
└── rules/                  # YAML cheat sheet definitions
```
