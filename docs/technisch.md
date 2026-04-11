# Technische documentatie — Xibo CMS Working Local

## Concept

Xibo CMS draait als Docker container op de VPS en beheert alle digitale schermen (displays) in de Working Local ruimte. Via een XMR push-verbinding worden inhoudsupdates real-time naar de Xibo Players gestuurd. Bezettingsdata van werkplekken wordt opgehaald via de Odoo JSON API.

## Architectuur

```
Internet
    │
    ▼
Cloudflare DNS (proxy UIT — XMR vereist directe verbinding)
    │
    ▼
Traefik → signage.workinglocal.be (poort 80/443)
    │
    ▼
xibo-cms container (Xibo CMS)
    │   ├── /web              → Beheerinterface
    │   ├── /api              → REST API voor players
    │   └── :9505             → XMR push (WebSocket, directe poort)
    │
    ▼
xibo-db container (MariaDB 10.11)
    │
    └── database: xibo

Externe integratie:
    Odoo API → https://odoo.workinglocal.be/api/workspaces/availability
```

## docker-compose.yml

```yaml
services:
  xibo-cms:
    image: xibosignage/xibo-cms:latest
    restart: unless-stopped
    ports:
      - "9505:9505"          # XMR push — directe host poort vereist
    environment:
      - MYSQL_HOST=xibo-db
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=xibo
      - CMS_SERVER_NAME=${XIBO_SERVER_NAME}
      - CMS_USE_HTTPS=true
      - XMR_HOST=xibo-cms
    volumes:
      - xibo-library:/var/www/cms/library   # Media bestanden
      - xibo-backup:/var/www/backup         # Database backups
    depends_on:
      - xibo-db

  xibo-db:
    image: mariadb:10.11    # MySQL 8.0 is NIET compatibel met Xibo client libraries
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=xibo
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - xibo-db:/var/lib/mysql

volumes:
  xibo-library:
  xibo-backup:
  xibo-db:
```

## Environment variables

| Variabele | Beschrijving |
|---|---|
| `XIBO_SERVER_NAME` | Hostnaam van de CMS server (bv. `signage.workinglocal.be`) |
| `MYSQL_USER` | MariaDB gebruikersnaam |
| `MYSQL_PASSWORD` | MariaDB wachtwoord |
| `MYSQL_ROOT_PASSWORD` | MariaDB root wachtwoord |

## XMR Push Protocol

Xibo gebruikt XMR (Xibo Message Relay) voor real-time push communicatie naar players:

- Poort `9505` is open op de VPS host (via UFW)
- Players verbinden rechtstreeks op `signage.workinglocal.be:9505`
- Cloudflare proxy moet **UIT** staan — Cloudflare blokkeert custom poorten
- XMR gebruikt ZeroMQ protocol (geen HTTP)

## DNS (Cloudflare)

```
Type:  A
Name:  signage
Value: 23.94.220.181
Proxy: DNS only (grijs wolkje) — VERPLICHT voor XMR poort 9505
```

## Volumes

| Volume | Inhoud | Belang |
|---|---|---|
| `xibo-library` | Alle geüploade media (video, afbeeldingen, widgets) | Kritiek — backup vereist |
| `xibo-backup` | CMS database backups | Kritiek |
| `xibo-db` | MariaDB database | Kritiek |

## Odoo integratie

Xibo haalt werkplekbezetting op via een Remote DataSet:

**API endpoint:**
```
GET https://odoo.workinglocal.be/api/workspaces/availability
```

**DataSet configuratie in Xibo:**
| Instelling | Waarde |
|---|---|
| Type | Remote DataSet |
| URL | `https://odoo.workinglocal.be/api/workspaces/availability` |
| Data path | `workspaces` |
| Refresh interval | 60 seconden |

**Respons (JSON):**
```json
{
  "workspaces": [
    {
      "id": 1,
      "name": "Stille zone",
      "type": "desk",
      "available": true,
      "capacity": 4,
      "is_occupied": false
    }
  ]
}
```

## Eerste login

Na installatie zijn de standaard credentials:
- **Gebruiker:** `xibo_admin`
- **Wachtwoord:** `password`

Wijzig dit wachtwoord onmiddellijk na het eerste inloggen.

## Upload limiet

Xibo CMS heeft een ingebouwde uploadlimiet van **2 GB** — geen extra configuratie nodig voor grote videobestanden.

## UFW firewall

Poort 9505 moet expliciet open zijn naast de standaard webpoorten:

```bash
ufw allow 9505/tcp comment "Xibo XMR push"
```
