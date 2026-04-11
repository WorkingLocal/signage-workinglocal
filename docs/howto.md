# Hoe gebruik ik Xibo CMS? — Working Local

## Wat is dit?

Xibo CMS beheert alle digitale schermen in de Working Local ruimte. Via de webinterface kan je media uploaden, lay-outs ontwerpen en inhoud plannen voor de schermen. De schermen halen live werkplekbezetting op via Odoo.

---

## Hoe deploy ik Xibo op de VPS?

### Stap 1 — Wachtwoorden genereren

```bash
openssl rand -base64 32   # kopieer voor MYSQL_PASSWORD
openssl rand -base64 32   # kopieer voor MYSQL_ROOT_PASSWORD
```

### Stap 2 — Deployen via Coolify

1. Ga naar **https://coolify.workinglocal.be**
2. Klik **New Resource → Docker Compose**
3. Plak de inhoud van `docker-compose.yml` uit deze repo
4. Stel de environment variables in:

   | Variabele | Waarde |
   |---|---|
   | `XIBO_SERVER_NAME` | `signage.workinglocal.be` |
   | `MYSQL_USER` | `xibo` |
   | `MYSQL_PASSWORD` | gegenereerd wachtwoord |
   | `MYSQL_ROOT_PASSWORD` | gegenereerd wachtwoord |

5. Domein instellen: `https://signage.workinglocal.be`
6. Klik **Deploy**

### Stap 3 — DNS instellen in Cloudflare

Voeg een A-record toe:
- **Type:** A
- **Naam:** signage
- **Waarde:** `23.94.220.181`
- **Proxy:** UIT (grijs wolkje) — **verplicht** voor XMR poort 9505

### Stap 4 — XMR poort openzetten op de VPS

```bash
ssh root@23.94.220.181
ufw allow 9505/tcp comment "Xibo XMR push"
ufw status
```

---

## Hoe log ik voor het eerst in?

1. Ga naar **https://signage.workinglocal.be**
2. Log in met de standaard credentials:
   - **Gebruiker:** `xibo_admin`
   - **Wachtwoord:** `password`
3. Ga naar **Gebruikersbeheer → Profiel** en wijzig het wachtwoord

---

## Hoe voeg ik een scherm toe?

1. Ga naar **Displays → Displays**
2. Klik **Toevoegen**
3. Op het scherm/apparaat: installeer de **Xibo Player** app
4. Open de Player app en voer de CMS URL in: `https://signage.workinglocal.be`
5. Noteer de weergegeven **Display Code**
6. In de CMS: ga naar **Displays → Toevoegen** en voer de code in
7. Het scherm verschijnt in de lijst — klik **Goedkeuren**

---

## Hoe upload ik media?

1. Ga naar **Library → Library**
2. Klik **Uploaden**
3. Sleep bestanden in het uploadvenster (maximaal **2 GB** per bestand)
4. Geef het bestand een naam en klik **Opslaan**

Ondersteunde formaten: video (MP4, etc.), afbeeldingen (JPG, PNG), HTML, PowerPoint (via conversie).

---

## Hoe maak ik een lay-out?

1. Ga naar **Design → Layouts**
2. Klik **Toevoegen**
3. Kies een resolutie (bv. 1920×1080)
4. Voeg regio's toe en sleep media of widgets in de tijdlijn
5. Klik **Publiceren** als de lay-out klaar is

---

## Hoe koppel ik de werkplekbezetting van Odoo?

### DataSet aanmaken

1. Ga naar **Library → DataSets**
2. Klik **Toevoegen → Remote DataSet**
3. Vul in:
   - **Naam:** `Werkplekken Beschikbaarheid`
   - **URL:** `https://odoo.workinglocal.be/api/workspaces/availability`
   - **Data path:** `workspaces`
   - **Refresh:** `60` seconden
4. Klik **Opslaan**

### Kolommen instellen

Voeg kolommen toe die overeenkomen met het JSON antwoord:
- `id` (Number)
- `name` (String)
- `available` (String)
- `is_occupied` (String)
- `capacity` (Number)

### DataSet gebruiken in een lay-out

1. Open een lay-out in de editor
2. Voeg een **DataSet View** of **DataSet Ticker** widget toe
3. Selecteer de aangemaakte DataSet
4. Configureer de weergave naar wens

---

## Hoe plan ik content voor een scherm?

1. Ga naar **Scheduling → Agenda**
2. Klik **Toevoegen**
3. Kies:
   - **Display:** het gewenste scherm
   - **Lay-out:** de te tonen lay-out
   - **Datum/tijd:** beginuur en einduur (of permanent)
4. Klik **Opslaan**

---

## Problemen oplossen

| Probleem | Oplossing |
|---|---|
| Scherm toont "Not Authorised" | Display nog niet goedgekeurd in CMS → **Displays → Goedkeuren** |
| XMR verbinding mislukt | Controleer of poort 9505 open is: `ufw status` en Cloudflare proxy UIT |
| Player ontvangt geen updates | Controleer of XMR_HOST correct is ingesteld in de environment variables |
| DataSet toont geen data | Controleer of Odoo online is en de API data teruggeeft |
| Upload mislukt | Controleer bestandsgrootte — max 2 GB per bestand |
| CMS niet bereikbaar | Controleer of beide containers draaien in Coolify |
| Database fout bij opstart | Herstart de `xibo-db` container en daarna de `xibo-cms` container |
