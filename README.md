# HTML Exporter for Anki

**HTML Exporter for Anki** is an add-on that allows you to export the **Back side of selected Anki cards** into a clean, well-styled **HTML file**, preserving the original card CSS and images.  
The exported HTML can then be **printed or saved as PDF**, making it ideal for offline study, handouts, and archiving.

---

## 🔗 AnkiWeb Page

This add-on is officially published on **AnkiWeb**:

👉 https://ankiweb.net/shared/info/182840143

Installing from AnkiWeb is recommended for the easiest setup and automatic updates.

---

## 🎯 Features

- 📄 Export the **Back side only** of selected cards  
- 🎨 Preserve original **card CSS styling**  
- 🖼️ Include all images used in cards  
- 📁 Generate a **standalone HTML file**  
- 🖨️ **PDF-ready output** via browser print  
- 📚 Ideal for notes, handouts, and offline review  

---

## 🚀 How It Works

1. Select cards in the **Anki Browser**  
2. Use **Edit → Export selected cards to HTML**  
3. An HTML file is generated with:
   - Card content
   - Embedded CSS
   - Linked images
4. Open the HTML file in your browser
5. Print or export it as **PDF**

This workflow ensures maximum compatibility while keeping the add-on lightweight and dependency-free.

---

## 🖨️ PDF Export Workflow

This add-on does **not directly generate PDFs**.  
Instead, it provides **print-optimized HTML**, which can be converted to PDF using any modern browser.

### Recommended PDF Export Method

1. Open the exported `.html` file in Chrome / Edge / Firefox  
2. Press **Ctrl + P** (or Cmd + P on macOS)  
3. Select **Save as PDF**  
4. Adjust settings as needed:
   - Paper size (A4 / Letter)
   - Margins
   - Scale
   - Background graphics (recommended ON)
5. Save the PDF

This approach provides:
- Better layout control  
- Cross-platform consistency  
- No external PDF libraries required  

---

## 📦 Installation

### ⬇️ Install from AnkiWeb (Recommended)

1. Open Anki  
2. Go to **Tools → Add-Ons → Browse & Install**  
3. Search for **HTML Exporter for Anki**  
4. Install and restart Anki

### 📁 Manual Installation (GitHub)

1. Clone or download this repository  
2. Place it into:  
   `Anki2/addons21/anki-html-exporter`  
3. Restart Anki

---

## 🧪 Usage

### Export Selected Cards

1. Open **Browse**  
2. Select one or more cards  
3. Click **Edit → Export selected cards to HTML**  
4. Choose a file name  
5. Open the HTML file or export it as PDF

---

## ⚙️ Notes & Tips

- Images are copied next to the HTML file and referenced relatively  
- The export reflects **Anki’s card rendering**, not raw field text  
- Enable **“Background graphics”** in print settings for best PDF results  
- Large selections may take a few seconds to process

---

## 🛠 Troubleshooting

| Issue | Solution |
|------|----------|
| No cards exported | Ensure cards are selected in the Browser |
| Images missing | Check `collection.media` files |
| PDF layout issues | Adjust browser print scale / margins |
| Styles missing | Enable background graphics when printing |

---

## 📜 License

MIT License — Free to use, modify, and distribute.
