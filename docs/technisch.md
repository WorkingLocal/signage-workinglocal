# Technische documentatie — Xibo CMS Working Local

## Concept

Xibo CMS v4 draait als Docker stack op VPS-WORKINGLOCAL, beheerd via Coolify.
Via een XMR push-verbinding worden inhoudsupdates real-time naar de Xibo Players gestuurd.

## Architectuur v4

```
Internet
    │
    ▼
Cloudflare DNS (proxy UIT — XMR vereist directe verbinding)
    │
    ▼
Traefik → signage.qompanio.be (poort 80/443)
    │
    ▼
cms-web container (Xibo CMS v4.4.3)
    │   ├── /web              → Beheerinterface
    │   ├── /api              → REST API voor players
    │   └── → cms-xmr:9505   → XMR push (intern)
    │
    ├── cms-db (MySQL 8.4)   → database: cms
    ├── cms-xmr (v1.3)       → poort 9505 (host-binding voor players)
    ├── cms-memcached         → session/page cache
    └── cms-quickchart        → grafiek rendering

Photoframe:
    frame.workinglocal.be → photoframe-workinglocal (:8181)
    │   └── /data/photoframe/photos (406 foto's, rclone sync van ai-node-i9 02:00)

Uptime Kuma:
    uptime.workinglocal.be → uptime-kuma-wl (:3001)
    │   └── 7 monitors: frame, signage, coolify, odoo, metrics, focus, wordpress
```

## Layouts

| Layout | ID | Widget URL | Doel |
|---|---|---|---|
| Surface Hosting Local | 5 | http://127.0.0.1:8181/ | Surface Pro 4 woonkamer (lokale photoframe server) |
| Tablets Hosting Local | 7 | https://frame.workinglocal.be/ | Android tablets (Xibo Player) |

> ⚠️ Layouts zijn aangemaakt via directe SQL INSERT (niet via API) wegens complexiteit van Xibo v4 Draft-workflow voor regio's.

## docker-compose.yml (v4 — 5 containers)

```yaml
services:
  cms-db:
    image: mysql:8.4
    environment:
      MYSQL_DATABASE: cms
      MYSQL_USER: cms
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      MYSQL_RANDOM_ROOT_PASSWORD: "yes"

  cms-xmr:
    image: ghcr.io/xibosignage/xibo-xmr:1.3
    ports: ["9505:9505"]

  cms-memcached:
    image: memcached:alpine
    command: memcached -m 64

  cms-quickchart:
    image: ianw/quickchart

  cms-web:
    image: ghcr.io/xibosignage/xibo-cms:release-4.4.3
    environment:
      MYSQL_HOST: cms-db
      MYSQL_DATABASE: cms
      MYSQL_USER: cms
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
      XMR_HOST: cms-xmr
      CMS_USE_MEMCACHED: "true"
      MEMCACHED_HOST: cms-memcached
      CMS_SERVER_NAME: ${CMS_SERVER_NAME}
    volumes:
      - xibo-library:/var/www/cms/library
      - xibo-backup:/var/www/backup
      - xibo-custom-theme:/var/www/cms/web/theme/custom
```

## Environment variables

| Variabele | Beschrijving |
|---|---|
| `CMS_SERVER_NAME` | Hostnaam van de CMS server (`signage.qompanio.be`) |
| `MYSQL_PASSWORD` | MySQL wachtwoord voor user `cms` |

## Upgrade v3 → v4 (historisch — 2026-06-12)

- v3 gebruikte MariaDB 10.11 + single xibo-cms container van Docker Hub
- v4 gebruikt MySQL 8.4 + 5 containers van ghcr.io
- v4 is NIET beschikbaar op Docker Hub — altijd ghcr.io/xibosignage/ gebruiken
- Admin account aangemaakt via bcrypt SQL (password_hash PHP functie, csprng=2)
- OAuth2 client aangemaakt via SQL INSERT in oauth_clients/oauth_client_scopes

## XMR Push Protocol

- Poort `9505` is open op de VPS host (docker port binding in cms-xmr)
- Players verbinden op `signage.qompanio.be:9505`
- Cloudflare proxy moet **UIT** staan — Cloudflare blokkeert custom poorten
- XMR gebruikt ZeroMQ protocol (geen HTTP)

## DNS (Cloudflare)

```
Type:  A
Name:  signage
Value: 23.94.220.181
Proxy: DNS only (grijs wolkje) — VERPLICHT voor XMR poort 9505

Type:  A
Name:  frame
Value: 23.94.220.181
Proxy: DNS only

Type:  A
Name:  uptime
Value: 23.94.220.181
Proxy: DNS only
```

## Volumes

| Volume | Inhoud | Belang |
|---|---|---|
| `xibo-library` | Alle geüploade media (video, afbeeldingen, widgets) | Kritiek |
| `xibo-backup` | CMS database backups | Kritiek |
| `xibo-db` | MySQL database | Kritiek |
| `xibo-custom-theme` | Aangepaste thema bestanden | Laag |

## Eerste login / wachtwoord reset

Admin credentials: Vaultwarden → WorkingLocal → "Xibo CMS v4 - Admin"

Bij nood wachtwoord reset via bcrypt SQL (zie historische notes in git log).

## API Client (OAuth2)

Client ID: `xiboapi-v4`
Credentials: Vaultwarden → WorkingLocal → "Xibo CMS v4 - API Client"
Scopes: `all`, `design`, `designDelete`, `displays`, `schedule`
Grant type: `client_credentials`

Token ophalen:
```bash
curl -X POST https://signage.qompanio.be/api/authorize/access_token \
  -d "grant_type=client_credentials&client_id=xiboapi-v4&client_secret=SECRET"
```
