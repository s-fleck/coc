# Call of Cthulhu PDF Cheat Sheets

Generate beautiful, printable PDF cheat sheets for Call of Cthulhu RPG from YAML files. Create custom reference materials with support for icons, rich text formatting, and flexible layouts.

Based on the visual cheat sheets by `/u/Uncle_Bones_` from [this Reddit thread](https://www.reddit.com/r/callofcthulhu/comments/1aq0v34/visualised_cheat_sheets_for_combat_mechanics_i/). Most icons were created by `/u/Uncle_Bones_` and are used with permission.

## 📖 Download PDFs

**Ready-to-use cheat sheets** are available at: **[https://s-fleck.github.io/coc/](https://s-fleck.github.io/coc/)**

### Available Cheat Sheets

| Sheet                | Description                                                                                                      |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 🚶‍♂️ **Movement**      | Movement actions, sprinting, taking cover                                                                        |
| 🤸 **Evasion**       | Dodge mechanics and defensive maneuvers                                                                          |
| 🎯 **Firearms**      | Ranged combat, aiming, and shooting rules                                                                        |
| ⚔️ **Melee & Throw** | Close combat and throwing mechanics                                                                              |
| 🍀 **Pulp Luck**     | Luck point rules for Pulp Cthulhu ([reference](https://www.scribd.com/document/420748823/Pulp-Luck-Cheat-Sheet)) |

## ✨ Features

- **🎨 Professional Layout**: Clean, printer-friendly design optimized for table use
- **🔤 Unicode & Emoji Support**: Full support for special characters and emojis
- **🎨 Customizable Colors**: Configure all colors via `config.yml`
- **📝 Markdown Support**: Rich text formatting in descriptions
- **🖼️ Icon Support**: PNG and SVG icons with automatic scaling
- **📄 Flexible Sections**: Optional headers, multiple card types, smart layouts
- **🚀 GitHub Integration**: Automatic PDF generation and deployment

## 🚀 Quick Start

1. **Clone and setup**:

   ```bash
   git clone https://github.com/s-fleck/coc.git
   cd coc
   python -m venv .venv
   ```

2. **Activate environment and install dependencies**:

   ```bash
   # Windows
   .venv\Scripts\activate

   # Linux/Mac
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Generate PDFs**:

   ```bash
   python build_pdf.py
   ```

4. **View output**: Check the `output/` directory for generated PDFs

## 📁 Project Structure

```
├── .github/workflows/       # GitHub Actions for auto-deployment
├── docs/                   # GitHub Pages site
├── fonts/                  # Font files (see fonts/README.md)
├── img/                    # Icon assets
├── output/                 # Generated PDFs (local)
├── rules/                  # YAML cheat sheet definitions
├── build_pdf.py           # Main PDF generator
├── config.yml             # Color and style configuration
└── requirements.txt        # Python dependencies
```

## 🛠️ Creating Custom Cheat Sheets

1. **Create a YAML file** in the `rules/` directory
2. **Define your content** using the schema:
   ```yaml
   sheet:
     sections:
       - title: "Section Name"
         type: "mini_card" # or "full_card"
         items:
           - title: "Action Name"
             icon: "img/icon.png"
             description: "Action description with **markdown**"
             cost: "Cost or requirement"
   ```
3. **Run the generator**: `python build_pdf.py`
4. **Find your PDF** in the `output/` directory

For detailed documentation on the YAML schema, see the existing files in `rules/` as examples.

## 🤝 Contributing

**Contributions welcome!** This project is perfect for:

- 📋 Adding new cheat sheets for different game systems
- 🔧 Improving existing rules and corrections
- 🎨 Enhancing the PDF generator functionality
- 🐛 Bug fixes and optimizations

**Note**: Assets in `/img` and `/fonts` folders have specific licenses - please respect original creators' rights.

## 📝 Development Notes

All the python code in this project is 100% AI generated and therefore entirely monstrous and unknowable.
Nevertheless, it successfully produces high-quality, printable cheat sheets with all planned features.

Additional cheat sheets for Cthulhu Invictus and expanded Pulp Cthulhu content planned for 2025-2026. (maybe)

## 📄 License

Code is open source and you may do with it whatever you wish. Icon assets and fonts belong to their original creators.
