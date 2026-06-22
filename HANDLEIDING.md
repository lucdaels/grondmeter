# Grondmeter — Handleiding

Versie: 1.5 · Laatste update: juni 2026

---

## Wat is de app?

Grondmeter is een persoonlijke moestuin-app die:
- Grondmetingen registreert (vruchtbaarheid, vocht, pH, temperatuur, licht)
- Foto's analyseert via Claude AI en tuinadvies geeft
- Metingen opslaat in de cloud (Firebase) — bereikbaar op elk apparaat
- Werkt als PWA (installeerbaar op telefoon als echte app)

---

## Architectuur

```
Broncode (lokaal PC)
  ↓  uv run deploy.py
Firebase Hosting  →  https://grondmeter-koksijde.web.app
  ↕
Firebase Firestore  (metingen + bakken per gebruiker)
  ↕
Firebase Auth  (Google sign-in, alleen lucdaels@gmail.com)
```

### Lokale bestanden

| Bestand | Functie |
|---------|---------|
| `index.html` | Volledige app (HTML + CSS + JS, alles in één bestand) |
| `firebase-config.js` | Firebase projectconfiguratie (API-sleutel etc.) |
| `manifest.json` | PWA-manifest (icoon, naam, themakleur) |
| `deploy.py` | Deploy-script: uploadt bestanden naar Firebase Hosting |
| `server.py` | Lokale webserver voor ontwikkeling (poort 8080) |
| `start-server.bat` | Start de lokale server (dubbelklik) |
| `firestore.rules` | Beveiligingsregels voor Firestore (referentie) |
| `firebase.json` | Firebase Hosting configuratie |
| `.firebaserc` | Firebase project-ID (`reisapp-koksijde`) |

### Firebase project

Het Firebase project is **reisapp-koksijde** (gedeeld met de reisapp).
Grondmeter-data staat in aparte Firestore-collecties:

```
grondmeter/
  {uid}/
    metingen/
      {metingId}  →  { datum, bak, plant, fertility, moisture, ph, temp, light,
                        status, advies, fotoVer, fotoDicht }
    instellingen/
      profiel     →  { bakken: [...], bakInfo: {...} }
```

Elke gebruiker heeft zijn eigen `uid` en kan nooit data van anderen zien
(Firestore security rule: `request.auth.uid == uid`).

---

## App bijwerken en deployen

### 1. Broncode aanpassen

Bewerk `index.html` (of `firebase-config.js`, `manifest.json`) op de PC.

### 2. Lokaal testen

Dubbelklik op `start-server.bat` → open `http://localhost:8080` in de browser.

### 3. Deployen naar Firebase Hosting

Open PowerShell en voer uit:

```powershell
cd "C:\Users\ldaels\OneDrive - Gemeentebestuur Koksijde\Documenten\prive\grondmeter"
uv run --link-mode=copy deploy.py
```

Het script:
1. Genereert een OAuth2-token via het service account (`serviceAccountKey.json` in de reisapp-map)
2. Maakt een nieuwe versie aan in Firebase Hosting
3. Uploadt de drie bestanden (`index.html`, `firebase-config.js`, `manifest.json`)
4. Publiceert de release

Na ±10 seconden is de nieuwe versie live op `https://grondmeter-koksijde.web.app`.

> **Waarom `uv` en niet de Firebase CLI?**
> De Firebase CLI vereist een interactieve login via browser-OAuth die niet werkt op het
> bedrijfsnetwerk (proxy blokkeert de OAuth-callback). Het Python deploy-script gebruikt
> het service account direct via de REST API en werkt altijd.

### 4. Versie controleren in Firebase console

`https://console.firebase.google.com/project/reisapp-koksijde/hosting/sites/grondmeter-koksijde`

---

## App op telefoon installeren (PWA)

1. Open `https://grondmeter-koksijde.web.app` in Chrome op Android
2. Tik op de drie puntjes (⋮) → **Toevoegen aan startscherm**
3. De app verschijnt als icoon en opent zonder adresbalk (echte app-look)

Na een update: sluit de app volledig en open opnieuw — de browser laadt automatisch de nieuwe versie.

---

## Inloggen

De app vereist een Google-account. Enkel **lucdaels@gmail.com** heeft toegang.
Bij andere accounts: automatisch uitgelogd met melding "Geen toegang voor dit account."

Bij het eerste bezoek (of na uitloggen): groene login-overlay met Google-knop.
Na het inloggen: data wordt geladen vanuit Firestore.

Uitloggen: tab **Instellingen** → **Account** → **Afmelden**.

---

## Instellingen

### Claude API-sleutel
- Tab **Instellingen** → **Claude API** → plak je `sk-ant-...` sleutel → **Opslaan**
- De sleutel wordt opgeslagen in de browser (localStorage), nooit in Firestore of Firebase
- Modelkeuze: **Haiku 4.5** (goedkoper, sneller) of **Sonnet 4.6** (nauwkeuriger)

### Bakken beheren
- Tab **Instellingen** → **Bakken**
- Elke bak heeft een naam en een veld "Grondsamenstelling":
  - bijv. *"50 cm compost, veel regenwormen, geen kunstmest"*
  - bijv. *"Potgrond gemengd met perliet, zure pH"*
- Claude gebruikt de grondsamenstelling bij elke analyse voor die specifieke bak
- Bakken worden automatisch gesynchroniseerd naar Firestore via **Bakken opslaan**

---

## Meting nemen

1. Tik op **+** (overzicht) of tab **Meten**
2. Kies een bak + optioneel plantnaam
3. **Stap 1** — Foto van ver: plant herkennen
4. **Stap 2** — Foto van dicht: meter lezen  
   *Of: vul meetwaarden handmatig in (vruchtbaarheid, vocht %, pH, temperatuur, licht)*
5. **Analyseren** — Claude leest de meter, identificeert de plant, geeft advies
6. **Opslaan** — meting wordt bewaard in IndexedDB (lokaal) en Firestore (cloud)

### Wat Claude analyseert
- Plantnaam (van foto of handmatig ingevoerd)
- Meetwaarden (van foto of handmatig)
- Status: `ok` / `water` / `droog` / `mest` / `warn`
- Concreet advies in het Nederlands (water geven, bemesten, oogsten...)
- Historische trend: de laatste 5 metingen van die bak worden meegestuurd als context

### Opgeslagen per meting
- Datum en tijd (`Date.now()`)
- Bak en plantnaam
- Meetwaarden: vruchtbaarheid (0–3000), vocht (%), pH, temperatuur (°C), licht (lux)
- Status en advies
- Foto van ver en foto van dicht (gecomprimeerd: max 800×800px, JPEG 70%)
- In Firestore: foto's extra gecomprimeerd tot 500px voor documentlimiet (max 1 MB/doc)

---

## Gegevens bekijken

### Overzicht (startscherm)
- Laatste meting per bak, gesorteerd op datum
- Vochttrend als grafiekje (laatste 10 metingen)
- Tik op een kaart → detail overlay met beide foto's, alle waarden en advies

### Trends
- Alle metingen chronologisch, filterbaar per bak
- Tik op een meting voor detail

---

## Synchronisatie

| Actie | Lokaal (IndexedDB) | Firestore |
|-------|-------------------|-----------|
| App openen | geladen | data van Firestore overschrijft lokale data |
| Meting opslaan | ja | ja (asynchroon, op de achtergrond) |
| Meting verwijderen | ja | ja |
| Bakken opslaan | localStorage | ja |
| Sync-status | ☁ = ok · ↑ = bezig · ⚠ = fout | — |

Bij sync-fout: data blijft lokaal bewaard, volgende actie probeert opnieuw.

---

## Data exporteren / wissen

- Tab **Instellingen** → **Data** → **Exporteren**: download alle metingen als JSON
- Tab **Instellingen** → **Data** → **Alles wissen**: verwijdert lokale IndexedDB  
  *(Firestore-data blijft staan — bij heropenen wordt opnieuw gesynchroniseerd)*

---

## Firebase console

| Taak | URL |
|------|-----|
| Hosting releases | `https://console.firebase.google.com/project/reisapp-koksijde/hosting/sites/grondmeter-koksijde` |
| Firestore data bekijken | `https://console.firebase.google.com/project/reisapp-koksijde/firestore` |
| Auth gebruikers | `https://console.firebase.google.com/project/reisapp-koksijde/authentication/users` |
| Authorized domains | `https://console.firebase.google.com/project/reisapp-koksijde/authentication/settings` |

---

## Kosten

Beide apps (reisapp + grondmeter) delen het **reisapp-koksijde** Firebase project (Blaze pay-as-you-go).
Bij normaal gebruik van de grondmeter zijn de Firebase-kosten verwaarloosbaar (<€0,10/maand).

Claude API-kosten: ±€2/jaar bij 5–10 metingen per week met Sonnet 4.6.

---

## Veelgestelde vragen

**Moet mijn pc aan staan voor de app?**
Neen. De app staat op Firebase Hosting en werkt altijd, overal.

**Wat als ik de app verwijder van mijn startscherm?**
Metingen staan in Firestore — log opnieuw in en alles is er terug.

**Kan iemand anders mijn metingen zien?**
Neen. Firestore-rules zorgen dat alleen jouw Google-account (`lucdaels@gmail.com`) jouw data kan lezen.

**Wat als het bedrijfsnetwerk Firebase blokkeert?**
De app werkt op elke internetverbinding (ook mobiele data). Enkel het deploy-script draait op de PC.

**API-sleutel kwijt of gewijzigd?**
Aanpassen in Instellingen → Opslaan. Geen deploy nodig — sleutel staat alleen in de browser.
