# Xibo CMS — Working Local Setup

## Installatie

Xibo draait via de officiële Docker images van [xibosignage/xibo-docker](https://github.com/xibosignage/xibo-docker).

### Stappen

1. Clone de officiële xibo-docker repo op de VPS:
   ```bash
   cd /opt
   git clone https://github.com/xibosignage/xibo-docker.git xibo
   cd xibo
   ```

2. Kopieer de config template vanuit deze repo:
   ```bash
   cp /pad/naar/signage-workinglocal/config.env.template config.env
   nano config.env  # vul wachtwoorden in
   ```

3. Start Xibo:
   ```bash
   docker compose up -d
   ```

## Domein

- CMS: `signage.workinglocal.be`
- XMR push-poort: `9505` (moet open staan in firewall, geen Cloudflare proxy)

## Players

Zie [players.md](players.md) voor een overzicht van de aangesloten schermen en players.
