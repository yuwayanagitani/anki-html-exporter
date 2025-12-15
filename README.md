# 🌈📤 HTML Exporter (Back Side) for Anki

Export the **Back side of selected cards** from Anki’s Browser into a **beautiful, self-contained HTML file**, with styles and images preserved ✨

---

## 🎯 What this add-on does

This add-on recreates the **Back side HTML exactly as Anki renders it**, then bundles everything into **one readable HTML file**.

It automatically:

✅ Renders cards using Anki’s own engine (`card.answer()`)  
🎨 Embeds each note type’s **CSS** so styling stays accurate  
🧩 Extracts **only the Back side** (after `<hr id="answer">`)  
🖼 Copies all referenced **images** from Anki’s media folder  
📄 Combines multiple cards into **one clean HTML page**

---

## 🖱 How to use

1️⃣ Open **Browse** (Anki Browser)  
2️⃣ Select one or more cards  
3️⃣ Menu: **Edit → Export selected cards to HTML**  
4️⃣ Choose a file name (e.g. `selected_back.html`)  
5️⃣ Done! 🎉  
   - HTML file is created  
   - Images are copied next to it  

---

## 🧱 Output structure

Each card is wrapped like this:

```html
<div class="card">
  <style>
    /* note type CSS */
  </style>
  <div class="back">
    <!-- back side HTML -->
  </div>
</div>
```

✨ The result:
- Large, readable text
- Card-style layout
- Works offline
- Easy to share or archive

---

## 🖼 Image handling

- Scans HTML for: `src="filename"`
- Copies files from:
  - 📂 `Anki collection.media`
  - ➜ output folder
- Keeps relative paths intact

⚠️ Notes:
- `srcset`, CSS `url(...)`, or inline `data:` images are **not detected**
- Web-hosted images stay as external links

---

## 📍 Where the menu item lives

The exporter is added to:

➡ **Browser → Edit → Export selected cards to HTML**

(You can easily move it to another menu if desired.)

---

## 🧩 Files included

📄 `__init__.py`  
- Adds the Browser menu action  
- Handles file dialogs and errors  

📄 `exporter.py`  
- Renders Back side HTML  
- Injects CSS  
- Copies media files  

---

## 🚑 Troubleshooting

❓ **“No card selected”**  
👉 Select cards in Browser first

❓ **Images missing**  
👉 Check that images exist in Anki’s media folder  
👉 Make sure templates use `src="filename"`

❓ **Export error dialog**  
👉 Usually caused by:
- No write permission
- Invalid output path
- Missing media folder

---

## 💡 Use cases

📘 Print-ready study notes  
🖥 Offline HTML review  
📤 Sharing explanations with others  
🗂 Long-term archiving of card backs  

---

Enjoy exporting your cards in style 🌟  
