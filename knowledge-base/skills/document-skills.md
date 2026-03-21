# Document Skills — Práce s XLSX, DOCX, PDF, PPTX

## Přehled

Praktický průvodce manipulací s dokumenty v AI agentech. Pokrývá vytváření, editaci a validaci všech hlavních Office formátů.

**Klíčový princip:** Každý formát má specifické gotchas — tento guide je shrnuje, abyste neopakovali stejné chyby.

| Formát | Vytvoření | Editace | Knihovna/Nástroj |
|--------|-----------|---------|------------------|
| XLSX | openpyxl (Python) | openpyxl | Formule, ne hodnoty |
| DOCX | docx-js (JavaScript) | Unpack → XML → Pack | Tracked changes |
| PDF | LibreOffice konverze | Omezená | soffice --headless |
| PPTX | Unpack → XML → Pack | Unpack → XML → Pack | XML-based |

---

## XLSX — Excel (openpyxl)

**Trigger:** "vytvoř excel", "porovnej XLS", "spreadsheet", "tabulka", "openpyxl"

### Čtení souborů

```python
from openpyxl import load_workbook

# S formulemi (pro editaci)
wb = load_workbook('file.xlsx', data_only=False)

# S vypočtenými hodnotami (jen pro čtení!)
wb = load_workbook('file.xlsx', data_only=True)
# ⚠ NIKDY neuložit wb otevřený s data_only=True — formule se ztratí!

sheet = wb.active  # nebo wb['SheetName']
for row in sheet.iter_rows():
    for cell in row:
        print(cell.coordinate, cell.value)
wb.close()
```

### Vytvoření souboru

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet.title = "Model"

# Formule, NIKDY hardcoded výpočty
sheet['B10'] = '=SUM(B2:B9)'        # ✅ Správně
sheet['B10'] = sum(values)            # ❌ Špatně — ztratí se auditní stopa

# Cross-sheet reference
sheet['C5'] = "=Sheet2!A1"

wb.save('output.xlsx')
```

### Formátování (IB standard)

```python
from openpyxl.styles import Font, PatternFill

# Barvy textu
BLUE_INPUT = Font(color='0000FF')      # Hardcoded inputs
BLACK_FORMULA = Font(color='000000')   # Formule a výpočty
GREEN_LINK = Font(color='008000')      # Odkazy v rámci listu
RED_EXTERNAL = Font(color='FF0000')    # Externí odkazy

# Zvýraznění předpokladů
YELLOW_BG = PatternFill(start_color='FFFF00', fill_type='solid')

# Číselné formáty
cell.number_format = '$#,##0;($#,##0);-'   # Měna (záporné v závorkách, nuly jako -)
cell.number_format = '0.0%'                  # Procenta
cell.number_format = '0.0x'                  # Násobky (EV/EBITDA)
cell.number_format = '@'                     # Roky jako text (ne 2,024)
```

### Validace formulí (POVINNÁ)

```bash
python scripts/recalc.py output.xlsx
```

Vrátí JSON:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

Kontrolované chyby: `#REF!`, `#DIV/0!`, `#VALUE!`, `#NAME?`, `#NULL!`, `#NUM!`, `#N/A`

### Programatická validace

```python
wb_formulas = load_workbook('file.xlsx', data_only=False)
wb_values = load_workbook('file.xlsx', data_only=True)

excel_errors = ['#VALUE!', '#DIV/0!', '#REF!', '#NAME?', '#NULL!', '#NUM!', '#N/A']

for sheet_name in wb_values.sheetnames:
    ws_v = wb_values[sheet_name]
    ws_f = wb_formulas[sheet_name]
    for row in ws_v.iter_rows():
        for cell in row:
            formula_cell = ws_f[cell.coordinate]
            if isinstance(formula_cell.value, str) and formula_cell.value.startswith('='):
                pass  # Je to formule
            if isinstance(cell.value, str) and any(e in cell.value for e in excel_errors):
                print(f"ERROR: {sheet_name}!{cell.coordinate}: {cell.value}")
```

### Gotchas

| Problém | Řešení |
|---------|--------|
| `data_only=True` + uložení = ztráta formulí | Používat jen pro čtení |
| Cell indexing: pandas 0-based, Excel 1-based | DataFrame řádek 5 = Excel řádek 6 |
| Sloupec 64 = BL, ne BK | Ověřit column mapping |
| Cross-sheet ref na neexistující sheet | Ověřit existenci všech referencovaných sheets |
| Formule nejsou přepočtené | Vždy spustit `recalc.py` po uložení |

---

## DOCX — Word (docx-js pro nové, XML pro editaci)

**Trigger:** "vytvoř dokument", "word", "docx", "smlouva", "report"

### Nový dokument (docx-js / JavaScript)

#### Stránka (KRITICKÉ: default je A4, ne US Letter)

```javascript
const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: {
          width: 12240,   // 8.5" US Letter (DXA: 1440 = 1 inch)
          height: 15840   // 11"
        },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [/* obsah */]
  }]
});

Packer.toBuffer(doc).then(buf => fs.writeFileSync("doc.docx", buf));
```

#### Landscape (gotcha: předat portrait rozměry, docx-js je sám prohodí)

```javascript
size: {
  width: 12240,   // Krátká hrana (NE landscape šířka!)
  height: 15840,  // Dlouhá hrana
  orientation: PageOrientation.LANDSCAPE  // docx-js interně prohodí
}
```

#### Styly a nadpisy

```javascript
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }  // size v half-points (24 = 12pt)
    },
    paragraphStyles: [
      {
        id: "Heading1",           // MUSÍ být přesné ID pro override
        name: "Heading 1",
        run: { size: 32, bold: true, font: "Arial" },
        paragraph: {
          spacing: { before: 240, after: 120 },
          outlineLevel: 0         // POVINNÉ pro Table of Contents
        }
      }
    ]
  },
  sections: [/* ... */]
});
```

#### Seznamy (NIKDY unicode bullets)

```javascript
// ❌ ŠPATNĚ
new Paragraph({ children: [new TextRun("• Item")] })

// ✅ SPRÁVNĚ
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("Správná odrážka")]
      })
    ]
  }]
});
// Pozor: stejný reference = pokračující číslování, jiný = restart
```

#### Tabulky (DUAL WIDTH — povinné!)

```javascript
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };

new Table({
  width: { size: 9360, type: WidthType.DXA },    // Vždy DXA, NIKDY PERCENTAGE
  columnWidths: [4680, 4680],                      // Součet = šířka tabulky
  rows: [
    new TableRow({
      children: [
        new TableCell({
          borders: { top: border, bottom: border, left: border, right: border },
          width: { size: 4680, type: WidthType.DXA },   // Musí odpovídat columnWidths
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },  // CLEAR, ne SOLID
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [new Paragraph({ children: [new TextRun("Cell")] })]
        })
      ]
    })
  ]
})
```

#### Obrázky (type je POVINNÝ)

```javascript
new ImageRun({
  type: "png",                    // POVINNÉ: png, jpg, gif, bmp, svg
  data: fs.readFileSync("img.png"),
  transformation: { width: 200, height: 150 },
  altText: { title: "T", description: "D", name: "N" }  // Všechna 3 pole povinná
})
```

#### Page break (musí být v Paragraph)

```javascript
// ❌ new PageBreak()           // Standalone — nevalidní XML
// ✅ new Paragraph({ children: [new PageBreak()] })
```

### Editace existujícího DOCX (3 kroky)

#### 1. Rozbalení

```bash
python scripts/office/unpack.py document.docx unpacked/
```

Extrahuje ZIP, pretty-printne XML, sloučí sousední runy se stejným formátováním.

#### 2. Editace XML (`unpacked/word/document.xml`)

**Tracked changes — vložení:**
```xml
<w:ins w:id="1" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:t>nový text</w:t></w:r>
</w:ins>
```

**Tracked changes — smazání (KRITICKÉ: `<w:delText>`, ne `<w:t>`):**
```xml
<w:del w:id="2" w:author="Claude" w:date="2025-01-01T00:00:00Z">
  <w:r><w:delText>smazaný text</w:delText></w:r>
</w:del>
```

**Komentáře (markery MUSÍ být přímé potomky `<w:p>`, nikdy uvnitř `<w:r>`):**
```bash
python scripts/comment.py unpacked/ 0 "Text komentáře"
python scripts/comment.py unpacked/ 1 "Odpověď" --parent 0
```

```xml
<w:commentRangeStart w:id="0"/>
<w:r><w:t>komentovaný text</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```

**Smart quotes (pro profesionální typografii):**

| Entity | Znak |
|--------|------|
| `&#x2018;` | ' (levá jednoduchá) |
| `&#x2019;` | ' (pravá / apostrof) |
| `&#x201C;` | " (levá dvojitá) |
| `&#x201D;` | " (pravá dvojitá) |

#### 3. Zabalení

```bash
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```

Validuje, opravuje (durableId, xml:space), komprimuje XML.

### Validace

```bash
python scripts/office/validate.py document.docx
```

Kontroluje: XML well-formedness, unikátní ID, reference, content types, tracked changes strukturu, spárování komentářových markerů.

### Accept all tracked changes

```bash
python scripts/accept_changes.py input.docx output.docx
```

### Gotchas docx-js

| # | Pravidlo |
|---|---------|
| 1 | Nastavit page size explicitně (default A4) |
| 2 | Landscape: předat portrait rozměry |
| 3 | Nikdy `\n` — použít nový Paragraph |
| 4 | Nikdy unicode bullets — LevelFormat.BULLET |
| 5 | PageBreak musí být v Paragraph |
| 6 | ImageRun vyžaduje `type` |
| 7 | Tabulky: vždy DXA, nikdy PERCENTAGE |
| 8 | Dual widths: columnWidths + cell width |
| 9 | Součet columnWidths = šířka tabulky |
| 10 | Cell margins vždy nastavit |
| 11 | ShadingType.CLEAR, ne SOLID |
| 12 | Nikdy tabulky jako oddělovače — border na Paragraph |
| 13 | TOC vyžaduje HeadingLevel, ne custom styly |
| 14 | Override built-in stylů přesnými ID ("Heading1") |
| 15 | outlineLevel povinný pro TOC (0=H1, 1=H2) |

---

## PDF

**Trigger:** "PDF", "export do PDF", "konverze PDF"

### Konverze do PDF (LibreOffice)

```bash
# DOCX → PDF
python scripts/office/soffice.py --headless --convert-to pdf input.docx

# XLSX → PDF
python scripts/office/soffice.py --headless --convert-to pdf input.xlsx
```

### PDF → obrázky (Poppler)

```bash
pdftoppm -jpeg -r 150 document.pdf output_page
```

### Sandboxed prostředí (socket shim)

```python
from office.soffice import run_soffice, get_soffice_env

# LibreOffice v sandboxu — automatický socket shim
result = run_soffice(["--headless", "--convert-to", "pdf", "input.docx"])

# Nebo: env pro subprocess
env = get_soffice_env()
subprocess.run(["soffice", ...], env=env)
```

Automaticky detekuje blokované AF_UNIX sockety, zkompiluje C shim, aplikuje LD_PRELOAD.

---

## PPTX — PowerPoint

**Trigger:** "prezentace", "PowerPoint", "PPTX", "slides"

### Workflow (XML-based, stejný jako DOCX editace)

```bash
# 1. Rozbalení
python scripts/office/unpack.py presentation.pptx unpacked/

# 2. Editace XML souborů v unpacked/ppt/slides/

# 3. Zabalení
python scripts/office/pack.py unpacked/ output.pptx --original presentation.pptx

# Validace
python scripts/office/validate.py presentation.pptx
```

Struktura: `ppt/presentation.xml`, `ppt/slides/slide1.xml`, `ppt/_rels/`

---

## Validační infrastruktura (všechny formáty)

### BaseSchemaValidator

Společná validace pro DOCX, XLSX, PPTX:

| Kontrola | Popis |
|----------|-------|
| XML well-formedness | Parsuje všechny XML soubory |
| Namespaces | Kontroluje deklarace |
| Unique IDs | Komentáře, záložky, shapes, sheets |
| File references | Všechny .rels odkazují na existující soubory |
| Content types | Všechny soubory v [Content_Types].xml |
| XSD schema | Validace proti ECMA-376 |
| Whitespace | xml:space="preserve" na textu s mezerami |
| Relationship IDs | r:embed, r:link, r:id platné |

### Auto-repair

```python
repair_count = validator.repair()
```

Opravuje: durableId mimo rozsah, chybějící xml:space="preserve".

### Checklist před odevzdáním

- [ ] Všechny XML soubory se parsují
- [ ] Žádné broken references v .rels
- [ ] Všechny soubory v [Content_Types].xml
- [ ] Unikátní ID (komentáře, záložky)
- [ ] Tracked changes správně vnořené
- [ ] Smart quotes konvertované na XML entity
- [ ] Žádné `<w:t>` uvnitř `<w:del>`
- [ ] Komentářové markery spárované
- [ ] Zero formula errors (XLSX)

---

## Porovnání XLS souborů

**Trigger:** "porovnej XLS", "najdi rozdíly", "diff excel", "srovnej tabulky"

### Workflow

1. Načíst oba soubory s `data_only=False` (zachovat formule)
2. Iterovat sheet po sheetu, buňka po buňce
3. Porovnat: hodnoty, formule, formátování, komentáře
4. Výstup: report s rozdíly (sheet, cell, typ změny, stará vs nová hodnota)

```python
from openpyxl import load_workbook

wb1 = load_workbook('file1.xlsx', data_only=False)
wb2 = load_workbook('file2.xlsx', data_only=False)

differences = []
for sheet_name in set(wb1.sheetnames) | set(wb2.sheetnames):
    if sheet_name not in wb1.sheetnames:
        differences.append({"sheet": sheet_name, "type": "added_sheet"})
        continue
    if sheet_name not in wb2.sheetnames:
        differences.append({"sheet": sheet_name, "type": "removed_sheet"})
        continue

    ws1, ws2 = wb1[sheet_name], wb2[sheet_name]
    max_row = max(ws1.max_row or 0, ws2.max_row or 0)
    max_col = max(ws1.max_column or 0, ws2.max_column or 0)

    for row in range(1, max_row + 1):
        for col in range(1, max_col + 1):
            c1 = ws1.cell(row=row, column=col)
            c2 = ws2.cell(row=row, column=col)
            if c1.value != c2.value:
                differences.append({
                    "sheet": sheet_name,
                    "cell": c1.coordinate,
                    "old": c1.value,
                    "new": c2.value,
                    "type": "formula_change" if str(c1.value or '').startswith('=') else "value_change"
                })
```

---

## Konsolidace více XLS

**Trigger:** "konsoliduj", "slouč excely", "merge spreadsheets", "agreguj data"

### Workflow

1. Identifikovat společnou strukturu (headers, layout)
2. Načíst všechny soubory
3. Mapovat sloupce (fuzzy matching na headers)
4. Sloučit data s označením zdroje
5. Deduplikovat (volitelně)
6. Výstup: konsolidovaný XLSX s formulemi pro agregaci

```python
from openpyxl import load_workbook, Workbook

files = ['q1.xlsx', 'q2.xlsx', 'q3.xlsx', 'q4.xlsx']
consolidated = Workbook()
sheet = consolidated.active
sheet.title = "Consolidated"

current_row = 1
for i, f in enumerate(files):
    wb = load_workbook(f, data_only=True)
    ws = wb.active
    for row_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
        if i > 0 and row_idx == 1:
            continue  # Přeskočit header kromě prvního souboru
        for col_idx, value in enumerate(row, 1):
            sheet.cell(row=current_row, column=col_idx, value=value)
        # Přidat zdrojový soubor jako poslední sloupec
        sheet.cell(row=current_row, column=len(row) + 1, value=f)
        current_row += 1

consolidated.save('consolidated.xlsx')
```
