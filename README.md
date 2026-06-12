# Signage — Working Local

Xibo CMS voor digitale schermen in de coworking ruimte.

## Wat het doet

- **Digitale schermen** aansturen via Xibo CMS v4
- **Fotoframe democase** via frame.workinglocal.be (photoframe container + rclone sync)
- **Gecentraliseerd beheer** van alle displays via `signage.workinglocal.be`
- **Uptime monitoring** via `uptime.workinglocal.be` (Uptime Kuma)

## Displays

| Display | Locatie | Player | Layout |
|---|---|---|---|
| Microsoft Surface Pro 4 | WL Woonkamer (Hosting Local) | Chromium kiosk | Surface Hosting Local |
| Android tablet (Fully Kiosk) | Working Local | Xibo Player for Android (⏳ pending) | Tablets Hosting Local |

## Services

| Service | URL | Container |
|---|---|---|
| Xibo CMS v4 | signage.workinglocal.be | cms-web (ghcr.io/xibosignage/xibo-cms:release-4.4.3) |
| Photoframe | frame.workinglocal.be | photoframe-workinglocal |
| Uptime Kuma | uptime.workinglocal.be | uptime-kuma |

## Deployment

Draait op `signage.workinglocal.be` via Coolify op VPS-WORKINGLOCAL.

### Xibo CMS v4

Vereist:
- Coolify op de VPS (zie [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal))
- DNS A-record: `signage.workinglocal.be` → `23.94.220.181` (Cloudflare proxy UIT — vereist voor XMR poort 9505)

Stappen:
1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml`
3. Domein instellen: `signage.workinglocal.be`
4. Environment variabelen toevoegen vanuit `config.env.template`
5. Deploy

> **Let op:** Xibo v4 gebruikt **MySQL 8.4** (GEEN MariaDB) en is beschikbaar op **ghcr.io** (niet Docker Hub).
> Docker Hub image `xibosignage/xibo-cms:latest` is v3 — gebruik altijd het expliciete v4 tag.

### Photoframe

Zie [photoframe/README.md](photoframe/README.md) voor volledige setup.

### Uptime Kuma

Compose in `uptime-kuma/docker-compose.yml` — deployen op `/opt/uptime-kuma/` op de VPS.

## Stack

| Onderdeel | Technologie |
|---|---|
| CMS | Xibo CMS v4.4.3 |
| Database | MySQL 8.4 |
| Push-poort | 9505 (XMR — cms-xmr container) |
| Cache | Memcached (alpine) |
| Charts | QuickChart |
| Reverse proxy | Traefik (via Coolify) |
| Monitoring | Uptime Kuma v1 |

## Documentatie

- [docs/setup.md](docs/setup.md) — volledige deployment handleiding
- [docs/technisch.md](docs/technisch.md) — technische architectuur
- [docs/players.md](docs/players.md) — overzicht van displays en player hardware
- [photoframe/README.md](photoframe/README.md) — photoframe server setup

## Gerelateerde repositories

| Repo | Inhoud |
|---|---|
| [vps-workinglocal](https://github.com/WorkingLocal/vps-workinglocal) | Server setup & infrastructuur |
| [odoo-workinglocal](https://github.com/WorkingLocal/odoo-workinglocal) | Odoo CE + coworking addon |
| [focus-workinglocal](https://github.com/WorkingLocal/focus-workinglocal) | Focus Kiosk app |
| [metrics-workinglocal](https://github.com/WorkingLocal/metrics-workinglocal) | Grafana + Prometheus monitoring |
