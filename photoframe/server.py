#!/usr/bin/env python3
"""
Photoframe server — Working Local Signage
Serves a fullscreen photo slideshow with optional iCal calendar sidebar.
Photos are read from PHOTO_DIR (mounted volume, synced by rclone from homelab NAS).
"""
import os, json, random, threading, time, re
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timedelta, timezone

PHOTO_DIR   = Path(os.environ.get("PHOTO_DIR", "/app/photos"))
CONFIG_FILE = Path(os.environ.get("CONFIG_FILE", "/app/config.json"))
PORT        = int(os.environ.get("PORT", 8181))
EXTENSIONS  = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.JPG', '.JPEG', '.PNG'}

DEFAULT_CONFIG = {
    "interval": 12,
    "transition": 1.8,
    "ical_urls": [],
    "calendar_days": 7
}

_cal_cache = []
_cal_lock  = threading.Lock()

def load_config():
    if CONFIG_FILE.exists():
        try:
            return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text())}
        except Exception:
            pass
    return DEFAULT_CONFIG

def fetch_calendar(config):
    from icalendar import Calendar
    import urllib.request
    events = []
    now    = datetime.now(timezone.utc)
    cutoff = now + timedelta(days=config.get("calendar_days", 7))
    for url in config.get("ical_urls", []):
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                cal = Calendar.from_ical(r.read())
            for comp in cal.walk():
                if comp.name != 'VEVENT':
                    continue
                dtstart = comp.get('DTSTART')
                if not dtstart:
                    continue
                dt = dtstart.dt
                if not hasattr(dt, 'hour'):
                    dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
                elif dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if now <= dt <= cutoff:
                    events.append({"dt": dt.isoformat(), "summary": str(comp.get('SUMMARY', ''))})
        except Exception as e:
            events.append({"dt": "", "summary": f"[Fout: {e}]"})
    events.sort(key=lambda e: e["dt"])
    return events[:10]

def calendar_refresh_loop():
    while True:
        try:
            cfg = load_config()
            if cfg.get("ical_urls"):
                evts = fetch_calendar(cfg)
                with _cal_lock:
                    _cal_cache.clear()
                    _cal_cache.extend(evts)
        except Exception:
            pass
        time.sleep(900)

threading.Thread(target=calendar_refresh_loop, daemon=True).start()

HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta http-equiv="cache-control" content="no-store">
<title>Fotoframe</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
html { overflow:hidden; background:#000; height:100%; }
body { background:#000; width:100%; height:100%; overflow:hidden; font-family:'Segoe UI',sans-serif; }

.slide {
  position:absolute; top:0; right:0; bottom:0; left:0;
  background-size:cover; background-position:center; background-repeat:no-repeat;
  opacity:0; transition:opacity __TRANS__s ease-in-out;
}
.slide.active { opacity:1; }

#sidebar {
  position:fixed; right:0; top:0; bottom:0; width:340px;
  background:linear-gradient(to left, rgba(0,0,0,0.55) 80%, transparent);
  display:flex; flex-direction:column; align-items:flex-end;
  padding:40px 28px 40px 20px;
  z-index:10;
}
#clock { font-size:4rem; font-weight:200; color:#fff; letter-spacing:-1px; text-align:right; }
#date  { font-size:1.1rem; color:rgba(255,255,255,0.7); margin-top:4px; text-align:right; margin-bottom:32px; }
#events { width:100%; }
.event-day  { font-size:0.7rem; color:#F5B800; text-transform:uppercase; letter-spacing:1px; margin:14px 0 4px; }
.event-item { display:flex; align-items:flex-start; gap:8px; padding:6px 0; border-top:1px solid rgba(255,255,255,0.08); }
.event-time { font-size:0.75rem; color:rgba(255,255,255,0.55); min-width:38px; padding-top:2px; }
.event-title{ font-size:0.88rem; color:#fff; line-height:1.35; }
.no-events  { font-size:0.85rem; color:rgba(255,255,255,0.35); font-style:italic; }
</style>
</head>
<body>
<div id="s0" class="slide"></div>
<div id="s1" class="slide"></div>
<div id="sidebar">
  <div id="clock">00:00</div>
  <div id="date"></div>
  <div id="events"><div class="no-events">Kalender laden...</div></div>
</div>
<script>
var INTERVAL = __INTERVAL__;
var photos   = __PHOTOS_JSON__;
var idx=0, cur=0;

function show() {
  if(!photos.length) return;
  var next = cur===0 ? 1 : 0;
  var s    = document.getElementById('s'+next);
  var parts = photos[idx].split('/');
  var encoded = [];
  for(var i=0; i<parts.length; i++) encoded.push(encodeURIComponent(parts[i]));
  s.style.backgroundImage = "url('/photo/"+encoded.join('/')+"')";
  var slides = document.querySelectorAll('.slide');
  for(var j=0; j<slides.length; j++) slides[j].classList.remove('active');
  void s.offsetWidth;
  s.classList.add('active');
  cur=next; idx=(idx+1)%photos.length;
}

function loadCalendar() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', '/api/calendar');
  xhr.onload = function() {
    var el = document.getElementById('events');
    try {
      var events = JSON.parse(xhr.responseText);
      if(!events.length) { el.innerHTML='<div class="no-events">Geen aankomende afspraken</div>'; return; }
      var NL_DAYS   = ['zo','ma','di','wo','do','vr','za'];
      var NL_MONTHS = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'];
      var html='', lastDay='';
      for(var i=0; i<events.length; i++) {
        var ev = events[i];
        var dt = ev.dt ? new Date(ev.dt) : null;
        var dayKey = dt ? dt.toDateString() : 'onbekend';
        if(dayKey !== lastDay) {
          lastDay=dayKey;
          var label = dt ? NL_DAYS[dt.getDay()]+' '+dt.getDate()+' '+NL_MONTHS[dt.getMonth()] : 'Onbekend';
          html += '<div class="event-day">'+label+'</div>';
        }
        var allDay  = ev.dt && ev.dt.indexOf('00:00:00+00:00') >= 0;
        var h = dt ? dt.getHours() : 0;
        var m = dt ? dt.getMinutes() : 0;
        var timeStr = (dt && !allDay) ? (h<10?'0':'')+h+':'+(m<10?'0':'')+m : '';
        html += '<div class="event-item"><span class="event-time">'+timeStr+'</span><span class="event-title">'+ev.summary+'</span></div>';
      }
      el.innerHTML=html;
    } catch(e) { el.innerHTML='<div class="no-events">Kalender niet beschikbaar</div>'; }
  };
  xhr.onerror = function() { document.getElementById('events').innerHTML='<div class="no-events">Kalender niet beschikbaar</div>'; };
  xhr.send();
}

function tick() {
  var d=new Date();
  var h=d.getHours(), m=d.getMinutes();
  document.getElementById('clock').textContent=(h<10?'0':'')+h+':'+(m<10?'0':'')+m;
  var DAYS=['Zondag','Maandag','Dinsdag','Woensdag','Donderdag','Vrijdag','Zaterdag'];
  var MONTHS=['januari','februari','maart','april','mei','juni','juli','augustus','september','oktober','november','december'];
  document.getElementById('date').textContent=DAYS[d.getDay()]+' '+d.getDate()+' '+MONTHS[d.getMonth()]+' '+d.getFullYear();
}

if(photos.length) show();
loadCalendar();
setInterval(show, INTERVAL*1000);
setInterval(loadCalendar, 300000);
setInterval(tick, 1000); tick();
</script>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        path = self.path.split('?')[0]

        if path in ('/', ''):
            cfg    = load_config()
            photos = []
            if PHOTO_DIR.exists():
                for f in PHOTO_DIR.rglob('*'):
                    if f.is_file() and f.suffix in EXTENSIONS:
                        photos.append(str(f.relative_to(PHOTO_DIR)))
            random.shuffle(photos)
            html = (HTML
                .replace('__TRANS__',        str(cfg['transition']))
                .replace('__INTERVAL__',     str(cfg['interval']))
                .replace('__PHOTOS_JSON__',  json.dumps(photos)))
            self._respond(200, 'text/html; charset=utf-8', html.encode())

        elif path == '/api/photos':
            photos = []
            if PHOTO_DIR.exists():
                for f in PHOTO_DIR.rglob('*'):
                    if f.is_file() and f.suffix in EXTENSIONS:
                        photos.append(str(f.relative_to(PHOTO_DIR)))
            random.shuffle(photos)
            self._respond(200, 'application/json', json.dumps(photos).encode())

        elif path == '/api/calendar':
            with _cal_lock:
                data = list(_cal_cache)
            self._respond(200, 'application/json', json.dumps(data).encode())

        elif path.startswith('/photo/'):
            from urllib.parse import unquote
            fname = unquote(path[7:])
            try:
                fpath = (PHOTO_DIR / fname).resolve()
                if not str(fpath).startswith(str(PHOTO_DIR.resolve()) + '/'):
                    self._respond(403, 'text/plain', b'Forbidden')
                    return
            except Exception:
                self._respond(403, 'text/plain', b'Forbidden')
                return
            if fpath.is_file() and fpath.suffix in EXTENSIONS:
                ext = fpath.suffix.lower()
                ct  = ('image/jpeg' if ext in ('.jpg','.jpeg')
                       else 'image/png'  if ext == '.png'
                       else 'image/webp' if ext == '.webp'
                       else 'image/gif')
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Cache-Control', 'public, max-age=3600')
                self.end_headers()
                with open(fpath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._respond(404, 'text/plain', b'Not found')
        else:
            self._respond(404, 'text/plain', b'Not found')

    def _respond(self, code, ct, body):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    srv = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'Photoframe server ::{PORT} — {PHOTO_DIR}')
    srv.serve_forever()
