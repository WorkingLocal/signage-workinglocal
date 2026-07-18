# Xibo Windows Player — Installatie en configuratie

Gedetailleerd stappenplan om een cleane Windows 11 Pro installatie in te richten als dedicated Xibo Player voor `signage.qompanio.be`.

---

## Vereisten

| | Minimum | Aanbevolen |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 Pro 64-bit |
| CPU | Intel i3 (4e gen+) | Intel i5/i7 |
| RAM | 4 GB | 8 GB |
| Opslag | 10 GB vrij | SSD, 50 GB+ vrij |
| Netwerk | Ethernet of stabiel WiFi | Ethernet (kabel) |
| Resolutie | 1080p | 1080p of 4K |

---

## Stap 1 — Windows voorbereiden

### 1.1 Windows bijwerken

Start → Instellingen → Windows Update → Controleren op updates.
Installeer alle updates en herstart. Herhaal tot er geen updates meer zijn.

### 1.2 Automatisch aanmelden instellen

De player moet zelfstandig opstarten zonder inlogscherm.

1. `Win + R` → typ `netplwiz` → Enter
2. Vink **"Gebruikers moeten een gebruikersnaam en wachtwoord invoeren"** uit
3. Klik OK → voer het wachtwoord van het account in
4. Herstart en controleer of Windows automatisch inlogt

### 1.3 Energiebeheer uitschakelen

De pc mag nooit in slaapstand gaan.

1. Start → Instellingen → Systeem → Energie & slaapstand
2. Zet **Scherm uitschakelen** op **Nooit**
3. Zet **Slaapstand** op **Nooit**

Of via PowerShell (als beheerder):
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```

### 1.4 Schermbeveiliging uitschakelen

Start → Instellingen → Personalisatie → Vergrendelingsscherm → Schermbeveiliging → **Geen**

### 1.5 Windows Defender SmartScreen (optioneel)

Als de installatie wordt geblokkeerd:
Start → Instellingen → Privacy & beveiliging → Windows-beveiliging → App- en browserbeheer → Reputatiebeheer → zet op **Uit**

---

## Stap 2 — Xibo Player downloaden

1. Ga naar: https://github.com/xibosignage/xibo-dotnetclient/releases
2. Download de laatste stabiele release: **`XiboClient-4.x.x-x64.msi`**
   - Kies de `.msi` installer (niet de portable versie)
   - Kies `x64` voor 64-bit Windows

> **Let op:** Kies een versie die compatibel is met je CMS versie. Check de CMS versie via:
> `https://signage.qompanio.be` → Administration → About

---

## Stap 3 — Xibo Player installeren

1. Dubbelklik op het gedownloade `.msi` bestand
2. Als Windows SmartScreen blokkeert: klik **Meer info** → **Toch uitvoeren**
3. Volg de installer:
   - Accepteer de licentievoorwaarden
   - Installatiemap: standaard laten (`C:\Program Files\Xibo Player`)
   - Klik **Installeren**
4. Vink **"Xibo Player starten"** AAN na installatie
5. Klik **Voltooien**

---

## Stap 4 — Xibo Player configureren

⚠️ **Er is GEEN systeemvakicoontje voor de player zelf** (enkel de losse Watchdog, met alleen "Restore"/"Exit"), en rechtsklikken op het spelervenster doet niets — dat was de oude v3-werkwijze en klopt niet meer voor v4 R407+. Open het configuratiescherm ("Player Options") in plaats daarvan met:

```powershell
Start-Process "C:\Program Files (x86)\Xibo Player\XiboClient.exe" -ArgumentList "o"
```

(Xibo Player is oorspronkelijk een screensaver-programma; `o` is het commandolijn-argument dat rechtstreeks het Options-scherm opent i.p.v. de fullscreen player.)

### 4.1 CMS verbinding instellen

| Veld | Waarde |
|---|---|
| **CMS Address** | `https://signage.qompanio.be` |
| **CMS Key** | **verplicht**, niet leeg laten — de "Server Key" uit Instellingen → Netwerk in het CMS (of `SELECT value FROM setting WHERE setting='SERVER_KEY';` in de CMS-database). Zonder correcte key: foutmelding "The Server key you entered does not match with the server key at this address". |

### 4.2 Display instellingen

| Veld | Waarde |
|---|---|
| **Display Name** | Beschrijvende naam, bv. `Inkom Working Local` |
| **Orientation** | Landscape (standaard) of Portrait |
| **Screenshot Interval** | 60 seconden (voor monitoring in CMS) |

### 4.3 XMR push instellen

| Veld | Waarde |
|---|---|
| **XMR Public Address** | `tcp://signage.qompanio.be:9505` |

> Dit veld is normaal automatisch ingesteld door het CMS na de eerste verbinding. Controleer of het correct is.

### 4.4 Opslaan en verbinden

Klik **Save** → de player probeert verbinding te maken met het CMS.

---

## Stap 5 — Display autoriseren in het CMS

Wanneer de player voor het eerst verbinding maakt, verschijnt hij als **"Awaiting Authorisation"** in het CMS.

1. Log in op `https://signage.qompanio.be`
2. Ga naar **Displays** (linkermenu)
3. Zoek het nieuwe display met status **"Awaiting Authorisation"**
4. Klik op het tandwiel-icoon → **Authorize**
5. Geef het display een naam en locatie (bv. `Inkom`, `Vergaderzaal 1`)
6. Klik **Save**

De player downloadt nu de standaard layout en begint met weergeven.

---

## Stap 6 — Player automatisch opstarten met Windows

### Optie A — Autostart via Taakplanner (aanbevolen)

1. `Win + R` → typ `taskschd.msc` → Enter
2. Rechtermuisknop op **Taakplanner-bibliotheek** → **Basistaak maken**
3. Naam: `Xibo Player Autostart`
4. Trigger: **Wanneer ik me aanmeld**
5. Actie: **Een programma starten**
6. Programma: `C:\Program Files\Xibo Player\Xibo.exe`
7. Vink aan: **Taak openen voor eigenschappen na voltooiing**
8. In eigenschappen → tabblad **Algemeen**:
   - Vink aan: **Uitvoeren met de hoogste bevoegdheden**
   - Configureren voor: **Windows 10** (ook voor Win 11)
9. Klik OK

### Optie B — Autostart via opstartmap

1. `Win + R` → typ `shell:startup` → Enter
2. Maak een snelkoppeling naar `C:\Program Files\Xibo Player\Xibo.exe`
3. Sleep de snelkoppeling naar de opstartmap

---

## Stap 7 — Volledig scherm en kioskinstelling

De Xibo Player draait standaard in volledig scherm. Controleer:

1. Start de player → hij zou het volledige scherm moeten innemen
2. Als er een taakbalk zichtbaar blijft:
   - Rechtermuisknop op taakbalk → **Taakbalkinstellingen** → **Taakbalk automatisch verbergen** inschakelen

### Kioskmodus (optioneel — volledig afgesloten systeem)

Als de pc puur als display-pc moet dienen zonder toegang tot Windows:

```powershell
# Toegewezen toegang instellen (kioskmodus)
# Start → Instellingen → Accounts → Gezin en andere gebruikers → Kioskmodus instellen
```

Of via Groepsbeleid:
- `gpedit.msc` → Gebruikersconfiguratie → Beheersjablonen → Systeem → **Ctrl+Alt+Del uitschakelen**

---

## Stap 8 — Verbinding testen

### In de Xibo Player

Het statusscherm (rechtermuisknop op player in systeemvak → **Status**) toont:

| Item | Verwachte waarde |
|---|---|
| CMS Last Seen | < 1 minuut geleden |
| Schedule Last Updated | Huidig tijdstip |
| XMR Connected | Yes |
| Display Status | Authorized |

### In het CMS

Displays → het display toont:

| Kolom | Verwachte waarde |
|---|---|
| Status | Groen bolletje |
| Last Accessed | < 5 minuten geleden |
| Logged In | Yes |

---

## Veelvoorkomende problemen

| Probleem | Oorzaak | Oplossing |
|---|---|---|
| Player toont "Not Authorised" | Display nog niet geautoriseerd in CMS | Zie stap 5 |
| Player kan CMS niet bereiken | Firewall of DNS-probleem | Controleer of `https://signage.qompanio.be` bereikbaar is in de browser op dezelfde pc |
| XMR niet verbonden | Poort 9505 geblokkeerd | Controleer bedrijfsfirewall/router voor TCP 9505 uitgaand |
| Scherm gaat uit na verloop | Energiebeheer actief | Herhaal stap 1.3 |
| Player start niet na herstart | Autostart niet ingesteld | Zie stap 6 |
| Zwart scherm na autorisatie | Geen layout toegewezen | Wijs een standaard layout toe in CMS → Displays → Display Groups |
| SmartScreen blokkeert installer | Windows beveiliging | Klik "Meer info" → "Toch uitvoeren" (zie stap 3) |
| "SSL certificate error" | Klok van de pc staat verkeerd | Synchroniseer de Windows-klok: `w32tm /resync` in CMD als beheerder |
