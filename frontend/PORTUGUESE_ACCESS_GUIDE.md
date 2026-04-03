# Portuguese (pt-BR) i18n Guide - Access & Testing

## ✅ Your Setup is Complete!

You now have Portuguese translations configured and running. Here's how to access them.

---

## 🌐 Accessing Your Portuguese Translations

### 1. **Development Server - Portuguese Locale**
```bash
npm run ng -- serve --configuration=pt-BR
# Server runs at: http://localhost:4200/
# All UI strings will appear in Portuguese
```

### 2. **Development Server - English (Default)**
```bash
npm run ng -- serve
# or
npm run ng -- serve --configuration=development
# Server runs at: http://localhost:4200/
# All UI strings will appear in English
```

### 3. **Production Build - Both Locales**
```bash
npm run ng -- build --localize
# Creates:
# ├── dist/supportai-frontend/     (English version)
# └── dist/supportai-frontend/pt-BR/ (Portuguese version)
```

---

## 🔍 Verifying Your Portuguese Translations

### In Browser
1. Open DevTools (F12)
2. Go to **Network** tab
3. Look for requests to `main-*.js`
4. Check the console for any i18n errors

### Translation Strings
When you serve with `--configuration=pt-BR`, you should see these Portuguese strings:

| English | Portuguese |
|---------|-----------|
| FAQ Drafts | Rascunhos de FAQ |
| Approve | Aprovar |
| Reject | Rejeitar |
| Service Unavailable | Serviço indisponível |
| The Problem | O Problema |
| Root Cause | Causa Raiz |

---

## 📂 File Structure

```
frontend/
├── src/
│  └── locale/
│     └── messages.pt-BR.xlf        ← Your Portuguese translations
│
├── dist/
│  ├── supportai-frontend/          ← English (default)
│  │  ├── index.html
│  │  ├── main-*.js
│  │  └── ...
│  │
│  └── supportai-frontend/pt-BR/    ← Portuguese
│     ├── index.html
│     ├── main-*.js
│     └── ...
│
└── angular.json                    ← Configuration
```

---

## 🛠️ How the Translation System Works

### 1. **Message Marking (Templates)**
Every UI string is marked with `i18n="@@messageId"`:
```html
<!-- faq-drafts-list.component.html -->
<a i18n="@@nav_faq_drafts">FAQ Drafts</a>
<button i18n="@@btn_approve">Approve</button>
```

### 2. **Translation File (XLF Format)**
Your `messages.pt-BR.xlf` contains translations:
```xml
<trans-unit id="nav_faq_drafts" datatype="html">
  <source>FAQ Drafts</source>
  <target state="translated">Rascunhos de FAQ</target>
</trans-unit>

<trans-unit id="btn_approve" datatype="html">
  <source>Approve</source>
  <target state="translated">Aprovar</target>
</trans-unit>
```

### 3. **Build Process**
When you build with `--configuration=pt-BR`:
- Angular extracts the Portuguese translations from `messages.pt-BR.xlf`
- Each JavaScript bundle includes the Portuguese strings compiled inline
- No runtime translation parsing needed

### 4. **Runtime Display**
The browser automatically loads the correct bundle:
- `/` → English version (default)
- `/pt-BR/` → Portuguese version (when deployed)

---

## 💻 Development Commands Cheat Sheet

### Build
```bash
# Build production (English only)
npm run ng -- build

# Build production with localization (all locales)
npm run ng -- build --localize

# Build Portuguese specifically
npm run ng -- build --configuration=pt-BR
```

### Serve (Development)
```bash
# Serve English (default)
npm run ng -- serve

# Serve Portuguese
npm run ng -- serve --configuration=pt-BR

# Serve with custom port
npm run ng -- serve --port 4201
npm run ng -- serve --configuration=pt-BR --port 4201
```

### Extract/Update Translations
```bash
# Extract all English source strings
npm run ng -- extract-i18n --project supportai-frontend

# This updates src/locale/messages.xlf
# You then manually translate into messages.pt-BR.xlf
```

---

## 📋 Your Portuguese Translation File

**Location**: `src/locale/messages.pt-BR.xlf`

This file contains all 40+ translated strings in XLF (XML Localization Format):

### Sample Structure:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2" xmlns="urn:oasis:names:tc:xliff:document:1.2">
  <file source-language="en" target-language="pt-BR">
    <body>
      <!-- Navigation -->
      <trans-unit id="nav_faq_drafts">
        <source>FAQ Drafts</source>
        <target>Rascunhos de FAQ</target>
      </trans-unit>
      
      <!-- Buttons -->
      <trans-unit id="btn_approve">
        <source>Approve</source>
        <target>Aprovar</target>
      </trans-unit>
      
      <!-- Forms -->
      <trans-unit id="label_article_title">
        <source>Article Title</source>
        <target>Título do Artigo</target>
      </trans-unit>
      
      <!-- ... 35+ more translations ... -->
    </body>
  </file>
</xliff>
```

---

## 🎯 Testing Your Portuguese Translations

### Step 1: Start Portuguese Dev Server
```bash
npm run ng -- serve --configuration=pt-BR
```

### Step 2: Open in Browser
```
http://localhost:4200/
```

### Step 3: Verify Translations
Check these areas for Portuguese text:
- [ ] Navigation links (top-left sidebar)
  - "Rascunhos de FAQ" (FAQ Drafts)
  - "Problemas" (Issues)
  - "Arquivo" (Archive)
  - "Configurações" (Settings)

- [ ] Page title: "Rascunhos de FAQ"
- [ ] Button text: "Gerar / Regenerar FAQs"
- [ ] Table headers: Portuguese column names
- [ ] Form labels: Portuguese field names
- [ ] Error messages: Portuguese error text

### Step 4: DevTools Console
```javascript
// Check current locale
console.log(navigator.language);

// Check if translations loaded correctly
console.log('UI should be in Portuguese');
```

---

## 🚀 Next Steps

### To Add More Languages
1. Create new translation file: `src/locale/messages.{locale}.xlf`
2. Add locale to `angular.json`:
   ```json
   "locales": {
     "pt-BR": "src/locale/messages.pt-BR.xlf",
     "fr": "src/locale/messages.fr.xlf"  // Add this
   }
   ```
3. Add serve configuration:
   ```json
   "configurations": {
     "pt-BR": {
       "buildTarget": "supportai-frontend:build:pt-BR"
     },
     "fr": {
       "buildTarget": "supportai-frontend:build:fr"  // Add this
     }
   }
   ```

### To Update Portuguese Translations
1. Edit `src/locale/messages.pt-BR.xlf`
2. Find the `<trans-unit>` with the message ID you want to change
3. Update the `<target>` element:
   ```xml
   <trans-unit id="nav_faq_drafts">
     <source>FAQ Drafts</source>
     <target>New Portuguese Translation Here</target>
   </trans-unit>
   ```
4. Rebuild: `npm run ng -- build --configuration=pt-BR`

### To Add New UI Strings
1. Mark the new string in template:
   ```html
   <p i18n="@@new_message_id">New English Text</p>
   ```
2. Extract: `npm run ng -- extract-i18n --project supportai-frontend`
3. Add translation in `messages.pt-BR.xlf`
4. Rebuild

---

## ⚠️ Warning Notes

### "Workspace extension with invalid name (i18n) found"
This is just a warning and doesn't affect functionality. It's a known Angular CLI message.

### "HMR is disabled"
This warning appears because `outputHashing` is set to 'all'. This is fine for production builds.

---

## 📊 Current Configuration Status

```
✅ English (en)
   - Default locale
   - Source strings
   - Always available

✅ Portuguese (pt-BR)  
   - Full translations (40+ strings)
   - Build: npm run ng -- build --configuration=pt-BR
   - Serve: npm run ng -- serve --configuration=pt-BR
   - File: src/locale/messages.pt-BR.xlf

🔄 Ready to Add More Locales
   - Spanish (es) - translation skeleton exists
   - French (fr)  - add when ready
   - German (de)  - add when ready
```

---

## 🔗 Quick Reference

| Task | Command |
|------|---------|
| Serve Portuguese | `npm run ng -- serve --configuration=pt-BR` |
| Build Portuguese | `npm run ng -- build --configuration=pt-BR` |
| Build All Locales | `npm run ng -- build --localize` |
| Serve English | `npm run ng -- serve` |
| Extract Strings | `npm run ng -- extract-i18n --project supportai-frontend` |
| Update Translation | Edit `src/locale/messages.pt-BR.xlf` then rebuild |

---

## 💡 Pro Tips

1. **Keep Terminal Open**: Keep a terminal running `npm run ng -- serve --configuration=pt-BR` while developing
2. **Hot Reload**: Changes to templates will automatically reload, rebuild with updated structures as needed
3. **Translation Quality**: Have native Portuguese speakers review your translations for accuracy
4. **Test All Pages**: Navigate through all app pages to verify all strings translate correctly
5. **Check RTL**: If adding RTL languages (Arabic, Hebrew) later, test RTL layout separately

---

## 📞 Troubleshooting

### Build Fails with Portuguese
```bash
# Clean and rebuild
rm -rf dist/
npm run ng -- build --configuration=pt-BR
```

### Strings Not Translating
1. Verify `messages.pt-BR.xlf` has the `<target>` tag filled in
2. Check message ID matches between template and XLF file
3. Rebuild the project

### Port Already in Use
```bash
# Use different port
npm run ng -- serve --configuration=pt-BR -- --port 4201
```

### Still See English Text
1. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Rebuild: `npm run ng -- build --configuration=pt-BR`

---

**Status**: ✅ Portuguese (pt-BR) Fully Configured and Working!

Your translations are accessible via:
- **Development**: `npm run ng -- serve --configuration=pt-BR`
- **Production**: Separate locale bundles in `dist/supportai-frontend/pt-BR/`
