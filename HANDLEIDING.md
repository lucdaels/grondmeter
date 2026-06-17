# Grondmeter — Handleiding

## Architectuur

```
PC (broncode)  →  GitHub (opslag)  →  GitHub Pages (live website)
index.html         lucdaels/grondmeter    lucdaels.github.io/grondmeter
```

Elke keer dat je de code aanpast op je pc, moet je hem via git naar GitHub pushen.
GitHub Pages publiceert automatisch de nieuwe versie binnen 1-2 minuten.

---

## Wijzigingen publiceren

### Snelste manier — dubbelklik op:
`c:\Users\ldaels\Documents\prive\grondmeter\nieuwe code saven.bat`

Dit doet automatisch: git add → commit → push.

### Of manueel via PowerShell:
```bash
cd c:\Users\ldaels\Documents\prive\grondmeter
git add index.html
git commit -m "Beschrijving van wat ik gewijzigd heb"
git push
```

Na 1-2 minuten is de nieuwe versie live. Status volgen:
`https://github.com/lucdaels/grondmeter/actions`

---

## App gebruiken op telefoon

URL: `https://lucdaels.github.io/grondmeter`

Na een update: sluit de app volledig en open opnieuw — hij laadt automatisch de nieuwe versie.

---

## Instellingen in de app

### API-sleutel (Claude)
- Tab **Instellingen** → API-sleutel → plak je `sk-ant-...` sleutel → Opslaan
- Sleutel staat lokaal op je telefoon, nooit op GitHub
- Kies model: **Haiku 4.5** (goedkoper) of **Sonnet 4.6** (nauwkeuriger voor meterwaarden)

### Bakken beheren
- Tab **Instellingen** → Bakken
- Elke bak heeft twee velden:
  - **Naam** — bijv. "Compost 1", "Potgrond 2"
  - **Grondsamenstelling** — beschrijving van de grond in die bak
    bijv. *"50cm compost, veel regenwormen, nooit kunstmest"*
    bijv. *"50cm potgrond gemengd met perliet, zure pH"*
- Claude gebruikt de grondsamenstelling bij elke analyse voor dat bak

---

## Meting nemen

1. Tik op **+** (overzicht) of tab **Meten**
2. Kies een bak
3. Foto van ver — plant herkennen
4. Foto van dicht — meter lezen (of vul waarden handmatig in)
5. Claude analyseert en geeft advies
6. Opslaan

### Wat wordt opgeslagen per meting:
- Datum en tijd
- Bak en plantnaam
- Alle meetwaarden: vruchtbaarheid, vocht %, pH, temperatuur, licht
- Volledig advies van Claude
- Beide foto's (verkleind opgeslagen op je telefoon)

---

## Veelgestelde vragen

**Moet mijn pc aan staan voor de app?**
Neen. De app staat online op GitHub Pages en werkt altijd.

**Zijn mijn metingen veilig?**
Ja. Metingen staan lokaal op je telefoon (IndexedDB), nooit op GitHub.

**Wat kost de AI-analyse?**
±€2 per jaar bij normaal gebruik (5-10 metingen per week) met Sonnet 4.6.

**Wat als ik de API-sleutel wijzig?**
Gewoon aanpassen in Instellingen → Opslaan. Geen push nodig.

**Hoe verwijder ik de app van mijn startscherm?**
Houd het icoon ingedrukt → "Verwijderen".
Herinstalleren: open `https://lucdaels.github.io/grondmeter` in Chrome → drie puntjes → Toevoegen aan startscherm.
