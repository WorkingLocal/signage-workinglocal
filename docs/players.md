# Xibo Players — Working Local

## Displays

| Display | Locatie | webOS versie | Xibo licentie |
|---|---|---|---|
| LG 65UH5E-B (65") | Eigen labo | 4.0 | Betaald |
| LG 55UH5F-H (55") | Eigen test | 4.1 | Betaald |
| LG 55UH5F-H (55") | Klant | 4.1 | Betaald |
| LG 75UL3J-E (75") | Klant | 6.0 | Betaald |
| LG 75UL3J-E (75") | Klant | 6.0 | Betaald |

## Beschikbare players (gratis)

| Toestel | OS | Player | Locatie | Tailscale |
|---|---|---|---|---|
| Windows laptop (i5-4200, 16GB) | Windows 10 | Windows Player | — | — |
| Dell XPS 7575 (i7, 16GB) | Windows | Windows Player | HL Kiosk Dashboard | — |
| Mele kiosk (Win 11 Pro) | Windows 11 | Windows Player | HL Kiosk Touch | — |
| **Microsoft Surface Pro 4** | **Ubuntu 22.04** | **Linux AppImage 1.8** | **WL Woonkamer** | **100.77.163.65** |

### Surface Pro 4 — Ubuntu Player (Woonkamer Working Local)

- AppImage: `/opt/xibo-player/Xibo_Player-1_8-x86_64.AppImage`
- Start script: `/opt/xibo-player/start.sh`
- SSH: `xibo@100.77.163.65` (credentials in Vaultwarden → WorkingLocal)
- Display: `Working Local Surface Woonkamer` | HardwareKey: `XIBO-SURFACE-001`
- **Kritieke fix:** `export LD_PRELOAD=/lib/x86_64-linux-gnu/libgmodule-2.0.so.0`  
  AppImage bundelt Ubuntu 20.04 libgmodule; Ubuntu 22.04 system libgio vereist nieuwere versie.
- Actief als persoonlijk fotoframe (photoframe-server op poort 8181) + Outlook agenda sidebar

## Aanbevolen productie-hardware

**Dell OptiPlex 3040 Micro** — ~€87 (i3-6100T, VESA-monteerbaar)
- Linux Player (gratis)
