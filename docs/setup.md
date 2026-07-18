# Xibo CMS — Working Local Setup

## Overzicht

Xibo CMS draait als Docker container op VPS-WORKINGLOCAL, beheerd via Coolify.

- **URL:** `signage.qompanio.be`
- **Database:** MariaDB 10.11
- **XMR push-poort:** `9505` (direct, geen Cloudflare proxy)

## Deployment via Coolify

1. In Coolify: **New Resource → Docker Compose**
2. Plak de inhoud van `docker-compose.yml` uit deze repo
3. Stel het domein in: `signage.qompanio.be`
4. Voeg environment variabelen toe (zie `config.env.template`):
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_ROOT_PASSWORD`
5. Deploy

> **Let op:** Gebruik `mariadb:10.11` — MySQL 8.0 is niet compatibel met de Xibo CMS client libraries.

> **Let op:** Bind poort 8080 niet op de host — dit conflicteert met `coolify-proxy`. Coolify routeert intern via het Docker netwerk.

## Eerste login

Na installatie:
- **Gebruiker:** `xibo_admin`
- **Wachtwoord:** `password`

Wijzig dit wachtwoord onmiddellijk na het eerste inloggen.

## DNS (Cloudflare)

```
Type:  A
Name:  signage
Value: 23.94.220.181
TTL:   Auto
Proxy: DNS only (grijs wolkje) — vereist voor XMR poort 9505
```

## Xibo integratie met Odoo

Xibo haalt live bezettingsdata op via Odoo's JSON endpoint:
```
GET https://odoo.workinglocal.be/api/workspaces/availability
```

Zie [odoo-workinglocal](https://github.com/WorkingLocal/odoo-workinglocal/blob/main/docs/xibo-integration.md) voor de volledige integratie setup.
