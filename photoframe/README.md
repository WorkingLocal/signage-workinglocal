# Photoframe — Working Local Signage

Fullscreen fotoframe webapplicatie, gehost op de Xibo CMS VPS.  
Toegankelijk op `https://frame.workinglocal.be` voor alle displays en tablets.

## Architectuur

```
ai-node-i9 (homelab)          VPS (Amsterdam)
/mnt/fotos/frame/   ──rclone──▶  /data/photoframe/photos/
                                          │
                                  Docker container
                                  photoframe-workinglocal
                                  poort 8181 (intern)
                                          │
                                     Traefik
                                          │
                              https://frame.workinglocal.be
                                          │
                              ┌───────────┴────────────┐
                         Surface Pro 4            Android tablets
                         (Chromium kiosk)         (Fully Kiosk Browser)
```

## Functionaliteit

- **Foto slideshow**: foto's uit `/app/photos` (recursief), willekeurige volgorde, crossfade-transitie
- **Kalender sidebar**: optionele iCal-integratie (klok + datum + aankomende afspraken)
- **Responsief**: vult elk scherm, elke orientatie, elke resolutie automatisch
- **Eén URL voor alles**: portrait/landscape, hoge/lage resolutie — allemaal dezelfde URL

## Gebruik op displays

| Display | Configuratie |
|---|---|
| Surface Pro 4 Woonkamer | Chromium kiosk: `http://127.0.0.1:8181/` (lokale server) |
| Android tablets (Fully Kiosk) | Screensaver URL: `https://frame.workinglocal.be` |

## Foto's toevoegen / beheren

Foto's staan op **ai-node-i9** in `/mnt/fotos/frame/` (NFS export).  
Subdirectories zijn toegestaan (bijv. per fotoshoot).  
De sync naar de VPS loopt dagelijks om 02:00 via cron.

**Handmatige sync forceren:**
```bash
ssh root@100.107.226.24
/opt/photoframe-sync/rclone-sync.sh
```

**Sync log bekijken:**
```bash
tail -f /var/log/photoframe-sync.log
```

## Kalender instellen

Bewerk `/data/photoframe/config.json` op de VPS:

```json
{
  "interval": 12,
  "transition": 1.8,
  "ical_urls": ["https://outlook.live.com/owa/calendar/...ics"],
  "calendar_days": 7
}
```

Herstart na wijziging: `docker restart photoframe-workinglocal`

## Installatie (éénmalig)

### 1. Directories aanmaken op VPS

```bash
ssh root@100.107.226.24
mkdir -p /data/photoframe/photos
mkdir -p /opt/photoframe-sync
cp /data/photoframe/config.json /data/photoframe/config.json 2>/dev/null || \
  echo '{"interval":12,"transition":1.8,"ical_urls":[],"calendar_days":7}' \
  > /data/photoframe/config.json
```

### 2. rclone installeren

```bash
curl https://rclone.org/install.sh | sudo bash
rclone --version
```

### 3. SSH key aanmaken voor rclone (geen passphrase)

```bash
ssh-keygen -t ed25519 -f /root/.ssh/photoframe_rclone -N "" \
  -C "rclone photoframe vps@workinglocal.be"
# Kopieer public key naar ai-node-i9:
ssh-copy-id -i /root/.ssh/photoframe_rclone.pub hostinglocal@100.126.121.11
# Test verbinding:
ssh -i /root/.ssh/photoframe_rclone hostinglocal@100.126.121.11 "ls /mnt/fotos/frame/ | head -5"
```

### 4. rclone configureren

```bash
mkdir -p /etc/rclone
cp /opt/photoframe-sync/rclone.conf.template /etc/rclone/photoframe.conf
# Verifieer:
rclone --config /etc/rclone/photoframe.conf ls ai-node-i9:/mnt/fotos/frame | head -5
```

### 5. Sync script installeren

```bash
cp /opt/photoframe-sync/rclone-sync.sh /opt/photoframe-sync/rclone-sync.sh
chmod +x /opt/photoframe-sync/rclone-sync.sh
# Test:
/opt/photoframe-sync/rclone-sync.sh
ls /data/photoframe/photos | head -5
```

### 6. Cron instellen

```bash
cp /opt/photoframe-sync/cron.d-photoframe-sync /etc/cron.d/photoframe-sync
chmod 644 /etc/cron.d/photoframe-sync
# Verifieer:
crontab -l 2>/dev/null; cat /etc/cron.d/photoframe-sync
```

### 7. Docker container starten

```bash
cd /opt/photoframe-workinglocal
docker compose up -d --build
docker logs photoframe-workinglocal
# Test intern:
curl -s http://localhost:8181/api/photos | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{len(d)} fotos')"
```

### 8. DNS instellen (Cloudflare)

Voeg toe in Cloudflare (workinglocal.be zone):

| Type | Naam | Inhoud | Proxy |
|---|---|---|---|
| A | frame | 23.94.220.181 | Uit (grijs) |

### 9. Fully Kiosk configureren op Android tablets

1. Open Fully Kiosk Browser → Settings → Web Content Settings
2. **Start URL**: `http://homeassistant.local:8123` (HA dashboard, ongewijzigd)
3. **Screensaver / Daydream URL**: `https://frame.workinglocal.be`
4. **Screensaver Activation**: After X minutes of inactivity (aanbevolen: 2 min)
5. **Motion Detection**: Tap to wake (zodat HA dashboard terug verschijnt bij aanraking)

## Beheer

**Container status:**
```bash
docker ps | grep photoframe
docker logs photoframe-workinglocal --tail 20
```

**Handmatig herladen (na config wijziging):**
```bash
docker restart photoframe-workinglocal
```

**Foto count:**
```bash
find /data/photoframe/photos -type f | wc -l
```

**Schijfruimte:**
```bash
du -sh /data/photoframe/photos
```

## Troubleshooting

| Probleem | Oplossing |
|---|---|
| Geen foto's zichtbaar | Check sync log: `tail /var/log/photoframe-sync.log` |
| Container start niet | `docker logs photoframe-workinglocal` |
| SSL werkt niet | Check Traefik: `docker logs coolify-proxy \| grep frame` |
| Fotos verouderd | Handmatige sync: `/opt/photoframe-sync/rclone-sync.sh` |
| ai-node-i9 niet bereikbaar | Check Tailscale: `tailscale status \| grep ai-node-i9` |

## Relatie met Surface Pro 4

De Surface Pro 4 in de woonkamer draait een **lokale copy** van dezelfde photoframe server  
op `localhost:8181`, gevoed via NFS rechtstreeks van ai-node-i9.  
De VPS-versie (`frame.workinglocal.be`) dient de Android tablets en eventuele toekomstige displays.  
Beide servers gebruiken dezelfde `server.py` codebase.
