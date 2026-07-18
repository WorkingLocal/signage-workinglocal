# Xibo Players — Working Local

## Actieve displays

| Display | Locatie | Player | Layout | Status |
|---|---|---|---|---|
| Microsoft Surface Pro 4 | WL Woonkamer (Hosting Local) | Chromium kiosk → localhost:8181 | Surface Hosting Local (ID 5) | ✅ actief |
| Android tablet (Fully Kiosk) | Working Local | Xibo Player for Android | Tablets Hosting Local (ID 7) | ⏳ pending |

## Surface Pro 4 — Chromium kiosk (Woonkamer)

**Hardware:** Microsoft Surface Pro 4 (m3-6Y30, 4GB RAM) — scherm 2736×1824 (3:2)
**OS:** Ubuntu 22.04
**Tailscale:** 100.77.163.65
**SSH:** `xibo@100.77.163.65` (credentials in Vaultwarden → Infra folder)

**Configuratie:**
- Xibo Player was geïnstalleerd maar is verwijderd op 2026-06-07 (stabiliteitsproblemen op Skylake hardware)
- Chromium kiosk wijst naar `http://127.0.0.1:8181/` (lokale photoframe server)
- Autostart: `/home/xibo/.config/autostart/xibo.desktop`

```bash
# Chromium kiosk autostart commando:
bash -c "sleep 3 && echo xibo | sudo -S bash -c 'echo 7500 > /sys/class/backlight/intel_backlight/brightness' && chromium-browser --kiosk --noerrdialogs --disable-infobars --no-first-run http://127.0.0.1:8181/"
```

**Photoframe server:**
- `/opt/photoframe/server.py` (Python, poort 8181)
- NFS mount: `192.168.111.31:/mnt/fotos` → `/mnt/ai-fotos` (ai-node-i9)
- 406 foto's, 1.5GB — Anne De Geyter fotoshoots

**Xibo CMS layout:** "Surface Hosting Local" (ID 5) — webpage widget → `http://127.0.0.1:8181/`

> ℹ️ Xibo Player opnieuw installeren op Surface voor volledige democase coherentie (web player URL als alternatief voor localhost)

## Android tablets — Fully Kiosk (Pending)

**Doel:** Volledig Kiosk op Android tablets wijst naar Xibo Web Player URL

**Stappen:**
1. Download Xibo Player for Android (gratis, via Xibo website)
2. Installeer op tablet
3. CMS URL: `https://signage.qompanio.be`
4. Display registreren in CMS (accepteren via admin UI)
5. Layout "Tablets Hosting Local" toewijzen (ID 7)
   - Widget type: webpage → `https://frame.workinglocal.be/`

**Alternatief (Fully Kiosk zonder Xibo Player):**
> NIET doen voor de democase — de hele fotoframe setup is een Xibo CMS democase.
> Xibo Player gebruikt de web player URL vanuit de CMS, die intern frame.workinglocal.be serveert.

## Historisch: Xibo Player 1.8 AppImage (verwijderd 2026-06-07)

De Surface draaide eerder Xibo Player 1.8 als Linux AppImage.
Verwijderd vanwege:
- Regelmatige crashes en poortconflicten (9696)
- QtWebKit in v1.8 ondersteunt geen ES6 (const/let/async/arrow functions)
- XMLHttpRequest geblokkeerd vanuit embedded browser
- CSS `inset` shorthand niet ondersteund

**Fixes die destijds nodig waren (historisch):**
- `export LD_PRELOAD=/lib/x86_64-linux-gnu/libgmodule-2.0.so.0` — libgmodule versieconflict
- `export no_proxy='*'; export GIO_EXTRA_MODULES=/nonexistent` — libproxy abort
- JS herschreven naar ES5, foto-lijst inline gebakken in HTML

## Productie hardware-aanbeveling

**Dell OptiPlex 3040 Micro** — ~€87 (i3-6100T, VESA-monteerbaar)
- Linux Player (gratis)
- Stabiel, klein formaat, VESA-monteerbaar achter scherm
