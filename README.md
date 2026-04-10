# Signage — Working Local

Xibo CMS voor digitale schermen in de coworking ruimte.

## Wat het doet

- **Digitale schermen** aansturen via Xibo CMS
- **Live bezettingsdata** ophalen van Odoo via JSON endpoint
- **Gecentraliseerd beheer** van alle displays via `signage.workinglocal.be`

## Displays

| Model | Locatie | webOS |
|---|---|---|
| LG 65UH5E-B (65") | Eigen labo | 4.0 |
| LG 55UH5F-H (55") | Eigen test | 4.1 |
| LG 55UH5F-H (55") | Klant | 4.1 |
| LG 75UL3J-E (75") | Klant | 6.0 |
| LG 75UL3J-E (75") | Klant | 6.0 |

## Deployment

Draait op `signage.workinglocal.be` via Coolify op VPS-WORKINGLOCAL.

### Vereisten

- Coolify op de VPS (zie [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal))
- DNS A-record: `signage.workinglocal.be` → `23.94.220.181` (Cloudflare proxy UIT — vereist voor XMR poort 9505)

### Stappen

1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml`
3. Domein instellen: `signage.workinglocal.be`
4. Environment variabelen toevoegen:
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_ROOT_PASSWORD`
5. Deploy

> **Let op:** Gebruik `mariadb:10.11` — MySQL 8.0 is niet compatibel met de Xibo CMS client libraries.

### Eerste login

- Gebruiker: `xibo_admin`
- Wachtwoord: `password` — **direct wijzigen na eerste login**

## Odoo integratie

Xibo haalt live bezettingsdata op via het Odoo JSON endpoint:

```
GET https://odoo.workinglocal.be/api/workspaces/availability
```

Zie [odoo-workinglocal → xibo-integration.md](https://github.com/WorkingLocal/odoo-workinglocal/blob/main/docs/xibo-integration.md) voor de volledige integratie setup.

## Stack

| Onderdeel | Technologie |
|---|---|
| CMS | Xibo CMS |
| Database | MariaDB 10.11 |
| Push-poort | 9505 (XMR) |
| Reverse proxy | Caddy (via Coolify) |

## Documentatie

- [docs/setup.md](docs/setup.md) — volledige deployment handleiding
- [docs/players.md](docs/players.md) — overzicht van displays en player hardware

## Gerelateerde repositories

| Repo | Inhoud |
|---|---|
| [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal) | Server setup & infrastructuur |
| [odoo-workinglocal](https://github.com/WorkingLocal/odoo-workinglocal) | Odoo CE + coworking addon (bezettingsdata) |
| [focus-workinglocal](https://github.com/WorkingLocal/focus-workinglocal) | Focus Kiosk app |
| [metrics-workinglocal](https://github.com/WorkingLocal/metrics-workinglocal) | Netdata monitoring |
