"""Builds the hi-nova.com pages from src/: docs/ (what GitHub Pages serves) and preview/ (an Artifact preview, not committed).

Fill CONTACT and OPERATOR below once the owner gives them; until then the pages show highlighted placeholders.
"""
import html, json, os, pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"

CONTACT = os.environ.get("NOVA_CONTACT", "hi@hi-nova.com")  # forwards (ImprovMX) to Nova's Gmail (owner, 2026-11-14)
OPERATOR = os.environ.get("NOVA_OPERATOR", "Oren Lugashi")  # operates Nova; the Google developer account name (owner, 2026-11-14)
# The app's signing certificates (SHA-256). EAS's key signs the sideloaded APK and uploads to Play; add Google
# Play's app-signing key here once Play Console shows it (Setup → App signing).
SIGNING_CERTS = ["75:89:65:B2:6A:42:CF:59:F4:B9:E7:99:EB:9B:54:D6:38:2F:83:24:17:6D:CF:08:AC:1A:D2:A6:3C:A3:32:9D",
                 # Google Play's app-signing key (read from Play's signed universal APK, 2026-11-18)
                 "76:25:0F:71:86:C4:5E:DC:B5:D9:67:B7:C6:93:78:D0:22:20:F1:7D:FC:E8:A9:D9:CB:9A:CA:D9:4D:74:9D:BA"]
# Google Analytics 4 (owner, 2026-11-15). Empty: no analytics anywhere, and the policy says nothing about it.
GA_ID = os.environ.get("NOVA_GA_ID", "G-7MWNCDS4FL")  # property hi-nova.com, web stream (owner, 2026-11-15)
WHATSAPP = os.environ.get("NOVA_WHATSAPP", "https://chat.whatsapp.com/GicdUQKgHyyL1c5hftEtMw")  # the testers' WhatsApp group (owner, 2026-11-14)
# Nova's API: the request-access form posts to {API}/access-requests (owner, 2026-11-15).
API = os.environ.get("NOVA_API", "https://novaapi-production-ebd4.up.railway.app")

HEX = "M42.21 16.5Q50 12 57.79 16.5L75.11 26.5Q82.91 31 82.91 40L82.91 60Q82.91 69 75.11 73.5L57.79 83.5Q50 88 42.21 83.5L24.89 73.5Q17.09 69 17.09 60L17.09 40Q17.09 31 24.89 26.5Z"
N = "M37 64L37 41Q37 36 40.4 39.66L59.6 60.34Q63 64 63 59L63 36"

def badge(uid: str) -> str:
    return (f'<svg viewBox="0 0 100 100" aria-hidden="true"><defs>'
            f'<linearGradient id="g{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7FA9"/><stop offset="1" stop-color="#E8437E"/></linearGradient>'
            f'<mask id="m{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><path d="{HEX}" fill="#fff"/>'
            f'<path d="{N}" fill="none" stroke="#000" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></mask></defs>'
            f'<rect width="100" height="100" fill="url(#g{uid})" mask="url(#m{uid})"/></svg>')

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs>'
           '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7FA9"/><stop offset="1" stop-color="#E8437E"/></linearGradient>'
           f'<mask id="m" maskUnits="userSpaceOnUse" x="0" y="0" width="100" height="100"><path d="{HEX}" fill="#fff"/>'
           f'<path d="{N}" fill="none" stroke="#000" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></mask></defs>'
           '<rect width="100" height="100" fill="url(#g)" mask="url(#m)"/></svg>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600&family=Rubik:wght@500&display=swap">')

# Hebrew unless #en, or the visitor chose English before; the buttons switch and remember.
LANG_SCRIPT = """<script>
(function () {
  var root = document.documentElement;
  function set(l) {
    root.setAttribute('data-lang', l); root.lang = l; root.dir = l === 'he' ? 'rtl' : 'ltr';
    try { localStorage.setItem('nova-lang', l); } catch (e) {}
  }
  var saved = null;
  try { saved = localStorage.getItem('nova-lang'); } catch (e) {}
  set(location.hash === '#en' ? 'en' : location.hash === '#he' ? 'he' : (saved === 'en' ? 'en' : 'he'));
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-set-lang]');
    if (b) set(b.getAttribute('data-set-lang'));
  });
})();
</script>"""

# The app's NovaSky (components/NovaSky.tsx): glows (colour, size, x, y, opacity, duration, scale), drift as fractions of
# the glow itself; hexagons (size, x, opacity, duration, start offset, turn direction).
GLOWS = [('#5B2350', 1.6, 0.15, 0.10, 0.35, 21, 1.10, 0.05, 0.019),
         ('#E8437E', 1.1, 0.95, 0.05, 0.24, 16, 1.12, -0.091, 0.036),
         ('#FF7FA9', 0.8, 0.90, 0.95, 0.18, 23, 1.08, -0.075, -0.044)]
HEXES = [(0.26, 0.10, 0.10, 44, 0.15, 1), (0.16, 0.74, 0.08, 36, 0.60, -1),
         (0.38, 0.48, 0.06, 58, 0.35, 1), (0.11, 0.32, 0.12, 31, 0.82, -1)]

def sky() -> str:
    out = []
    for c, s, x, y, o, d, k, dx, dy in GLOWS:
        out.append(f'<span class="glow" aria-hidden="true" style="--c:{c};--s:{s};--x:{x};--y:{y};--o:{o};--d:{d}s;--k:{k};--dx:{dx};--dy:{dy}"></span>')
    for s, x, o, d, f, t in HEXES:
        out.append(f'<span class="rise" aria-hidden="true" style="--s:{s};--x:{x};--o:{o};--d:{d}s;--f:{f};--t:{t}">'
                   f'<svg viewBox="0 0 100 100"><path d="{HEX}"/></svg></span>')
    return "\n".join(out)

# Line icons in the app's style (mobile components/icons.tsx): thin round strokes on a 24-unit box.
def icon(paths: str) -> str:
    return (f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round">{paths}</svg>')

ICONS = {
    # A page with a folded corner and lines (new, in the app's style).
    "doc": icon('<path d="M7 3.5h7l4.5 4.5v11a1.5 1.5 0 0 1-1.5 1.5H7A1.5 1.5 0 0 1 5.5 19V5A1.5 1.5 0 0 1 7 3.5z"/><path d="M13.5 3.5V8.5h5M9 12.5h6M9 16h4.5"/>'),
    # A speech bubble (new).
    "chat": icon('<path d="M4.5 6.5A2.5 2.5 0 0 1 7 4h10a2.5 2.5 0 0 1 2.5 2.5v7A2.5 2.5 0 0 1 17 16h-6.5L6 19.5V16h-1A1.5 1.5 0 0 1 3.5 14.5"/><path d="M8.5 9h7M8.5 12h4.5"/>'),
    # The app's mic.
    "mic": icon('<rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v2.5M9 20.5h6"/>'),
    # A calendar (new).
    "calendar": icon('<rect x="4" y="5.5" width="16" height="14.5" rx="2.2"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4M8.5 14h2.5"/>'),
    # The app's people, share and lock; and its lightbulb (a thought).
    "people": icon('<circle cx="9" cy="8" r="3.2"/><path d="M3 19.5c.6-3.3 3-5.2 6-5.2s5.4 1.9 6 5.2"/><path d="M15.5 5a3 3 0 0 1 0 6M17.5 14.6c1.9.6 3.1 2.3 3.5 4.9"/>'),
    "share": icon('<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.4M8.2 13.2l7.6 4.4"/>'),
    "lock": icon('<rect x="5" y="10.5" width="14" height="10" rx="2.2"/><path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3"/>'),
    "bulb": icon('<path d="M9 17.5h6M10 20.5h4M12 3.5a6 6 0 0 0-3.6 10.8c.6.5 1 1.2 1 2V17.5h5.2v-1.2c0-.8.4-1.5 1-2A6 6 0 0 0 12 3.5z"/>'),
    # A house (new).
    "home": icon('<path d="M4 11l8-6.5 8 6.5"/><path d="M6 9.5V19a1.5 1.5 0 0 0 1.5 1.5h9A1.5 1.5 0 0 0 18 19V9.5"/><path d="M10 20.5v-5h4v5"/>'),
    # A briefcase and a shield (new).
    "briefcase": icon('<rect x="3.5" y="7.5" width="17" height="12" rx="2.2"/><path d="M9 7.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v1.5M3.5 12.5h17M12 11.5v2"/>'),
    "shield": icon('<path d="M12 3.5l7 2.6v5.2c0 4.4-2.9 7.7-7 9.2-4.1-1.5-7-4.8-7-9.2V6.1z"/><path d="M9 12.2l2.2 2.2 4-4"/>'),
    # Two bubbles (a group chat) and an envelope (new).
    "group": icon('<path d="M3.5 6.5A2 2 0 0 1 5.5 4.5h8a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H9l-3.5 3v-3h0a2 2 0 0 1-2-2z"/><path d="M15.5 9h3a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2v3l-3.5-3h-4a2 2 0 0 1-2-1.6"/>'),
    "mail": icon('<rect x="3.5" y="5.5" width="17" height="13" rx="2.2"/><path d="M4 7l8 6 8-6"/>'),
}

# One primary call everywhere: request access (Stacy, 2026-11-18). A WhatsApp join leaves no Gmail address, so it
# can't become a Play tester: the group is offered after a request is sent, and as a quiet line in the final section.
def cta(small: bool = False) -> str:
    sm = " sm" if small else ""
    subject = "%D7%91%D7%A7%D7%A9%D7%94%20%D7%9C%D7%A0%D7%A1%D7%95%D7%AA%20%D7%90%D7%AA%20%D7%A0%D7%95%D7%91%D7%94"  # "בקשה לנסות את נובה"
    mail = f"mailto:{html.escape(CONTACT) if CONTACT else 'contact@hi-nova.com'}?subject={subject}"
    # Opens the request-access form; the email link is the fallback without script.
    return (f'<a class="btn{sm}" href="{mail}" data-access-open>{ICONS["mail"]}'
            '<span data-l="he">לבקש גישה לנובה</span><span data-l="en">Request access</span></a>')

def whatsapp_line() -> str:
    if not WHATSAPP:
        return ''
    wa = html.escape(WHATSAPP)
    return (f'<small data-l="he">כבר נרשמת? <a href="{wa}" target="_blank" rel="noopener">לקבוצת הבודקים בווטסאפ</a></small>'
            f'<small data-l="en">Already signed up? <a href="{wa}" target="_blank" rel="noopener">Join the testers\' WhatsApp group</a></small>')

# The hero conversation: questions across different documents, each answer with its source.
CHAT = {
    "he": [
        ("עד מתי ביטוח הרכב בתוקף?", "עד <strong>14 במרץ 2027</strong>", "פוליסת ביטוח רכב · עמוד 1"),
        ("כמה זמן מראש צריך להודיע לבעל הדירה שעוזבים?", "<strong>60 יום</strong> מראש, בכתב.", "חוזה שכירות · עמוד 4"),
        ("כמה הופרש לפנסיה בתלוש של אוקטובר?", "<strong>₪1,240</strong> מהמעסיק ו־<strong>₪1,050</strong> מהשכר.", "תלוש שכר, אוקטובר · עמוד 1"),
        ("האחריות על המקרר עדיין בתוקף?", "כן, עד <strong>3 ביוני 2027</strong>", "תעודת אחריות · עמוד 1"),
        ("כמה עלתה הצעת המחיר של הקבלן?", "<strong>₪86,000</strong> כולל מע״מ, בשלושה תשלומים.", "הצעת מחיר לשיפוץ · עמוד 2"),
        ("מתי פג הדרכון של נועה?", "ב־<strong>22 בינואר 2027</strong>", "דרכון · עמוד 1"),
    ],
    "en": [
        ("When does my car insurance run out?", "On <strong>14 March 2027</strong>", "Car insurance policy · page 1"),
        ("How much notice do we give the landlord before moving out?", "<strong>60 days</strong>, in writing.", "Lease agreement · page 4"),
        ("How much went to my pension on the October pay slip?", "<strong>₪1,240</strong> from the employer and <strong>₪1,050</strong> from the salary.", "Pay slip, October · page 1"),
        ("Is the fridge still under warranty?", "Yes, until <strong>3 June 2027</strong>", "Warranty certificate · page 1"),
        ("How much was the contractor's quote?", "<strong>₪86,000</strong> including VAT, in three payments.", "Renovation quote · page 2"),
        ("When does Noa's passport expire?", "On <strong>22 January 2027</strong>", "Passport · page 1"),
    ],
}

CHAT_SCRIPT = """<script>
(function () {
  var CHAT = %s;
  var chat = document.querySelector('[data-chat]');
  var log = chat && chat.querySelector('[data-log]');
  var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lang = function () { return document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'he'; };
  var timers = [], i = 0, onScreen = true, playing = false;
  function el(cls, htmlText) { var d = document.createElement('div'); d.className = cls; d.innerHTML = htmlText; return d; }
  function answer(ex) { return el('bubble a', '<span>' + ex[1] + '</span><span class="source">' + ex[2] + '</span>'); }
  function turn(ex, animate) {
    var t = el('turn', ''); var q = el('bubble q', ex[0]); if (animate) q.classList.add('enter');
    t.appendChild(q); if (!animate) t.appendChild(answer(ex)); return t;
  }
  function trim() { while (log.children.length > 3) log.removeChild(log.firstChild); }
  function later(fn, ms) { timers.push(setTimeout(fn, ms)); }
  function stop() { timers.forEach(clearTimeout); timers = []; playing = false; }
  function step() {
    if (!onScreen || document.hidden) { playing = false; return; }
    playing = true;
    var list = CHAT[lang()], ex = list[i %% list.length]; i++;
    var t = turn(ex, true); log.appendChild(t); trim();
    later(function () {
      var dots = el('typing enter', '<i></i><i></i><i></i>'); t.appendChild(dots);
      later(function () { t.removeChild(dots); var a = answer(ex); a.classList.add('enter'); t.appendChild(a);
        later(step, 3200); }, 1200);
    }, 700);
  }
  function reset() {
    if (!log) return;
    stop(); log.innerHTML = ''; i = 0;
    var list = CHAT[lang()];
    log.appendChild(turn(list[0], false)); i = 1;
    if (still) { log.appendChild(turn(list[1], false)); return; }
    later(step, 2400);
  }
  if (log) {
    reset();
    document.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('[data-set-lang]')) setTimeout(reset, 0); });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { onScreen = es[0].isIntersecting; if (onScreen && !playing && !still) { stop(); later(step, 600); } }).observe(chat);
    }
    document.addEventListener('visibilitychange', function () { if (!document.hidden && !playing && !still) { stop(); later(step, 600); } });
  }

  // The dock: visible between the hero and the final call to action.
  var dock = document.querySelector('[data-dock]'), hero = document.getElementById('top'), fin = document.getElementById('join');
  if (dock && hero && fin && 'IntersectionObserver' in window) {
    var heroIn = true, finIn = false;
    var update = function () { dock.hidden = heroIn || finIn; };
    new IntersectionObserver(function (es) { heroIn = es[0].isIntersecting; update(); }).observe(hero);
    new IntersectionObserver(function (es) { finIn = es[0].isIntersecting; update(); }).observe(fin);
  }
})();
</script>"""

def fill(body: str, uid: str) -> str:
    contact = html.escape(CONTACT) if CONTACT else '<span class="fill">[contact email]</span>'
    operator = html.escape(OPERATOR) if OPERATOR else '<span class="fill">[operator name]</span>'
    out = (body.replace("{{SKY}}", sky()).replace("{{BADGE_SMALL}}", badge(uid + "s")).replace("{{BADGE}}", badge(uid))
               .replace("{{CTA_BUTTONS_SMALL}}", cta(small=True)).replace("{{CTA_BUTTONS}}", cta()).replace("{{WHATSAPP_LINE}}", whatsapp_line())
               .replace("{{CHAT_SCRIPT}}", CHAT_SCRIPT % json.dumps(CHAT, ensure_ascii=False))
               .replace("{{ACCESS_POLICY_HE}}", ACCESS_POLICY["he"]).replace("{{ACCESS_POLICY_EN}}", ACCESS_POLICY["en"])
               .replace("{{CONTACT_RAW}}", html.escape(CONTACT) if CONTACT else "contact@hi-nova.com")
               .replace("{{CONTACT}}", f'<a href="mailto:{html.escape(CONTACT)}">{contact}</a>' if CONTACT else contact)
               .replace("{{OPERATOR}}", operator)
               .replace("{{COOKIE_LINK}}", ' · <a href="#" data-consent-open><span data-l="he">הגדרות עוגיות</span><span data-l="en">Cookie settings</span></a>' if GA_ID else '')
               .replace("{{SITE_POLICY_HE}}", SITE_POLICY["he"] if GA_ID else '')
               .replace("{{SITE_POLICY_EN}}", SITE_POLICY["en"] if GA_ID else ''))
    for name, svg in ICONS.items():
        out = out.replace("{{ICON_" + name + "}}", svg)
    assert "{{" not in out, out[out.index("{{"):out.index("{{") + 40]
    return out

SITE = "https://hi-nova.com"
# "path" is the page's public address; link previews (LinkedIn, WhatsApp, Facebook, X) read the og:/twitter: tags.
PAGES = {
    "index": {"title": "Nova נובה · העוזרת האישית שלך לניירת", "path": "/",
              "desc": "שואלים את נובה על המסמכים שלכם ומקבלים תשובה עם מקור. Ask Nova about your documents and get answers with sources."},
    "privacy": {"title": "Nova Privacy Policy", "path": "/privacy.html", "desc": "מדיניות הפרטיות של נובה. Nova's privacy policy."},
    "404": {"title": "Nova נובה", "path": "/", "desc": "נובה, העוזרת האישית שלך לניירת. Nova, your personal paperwork assistant."},
}
# The link-preview card: src/og.jpg, 1200x630 (scratchpad og/make_og.py renders it).
OG_IMAGE = {"path": "/og.jpg", "w": 1200, "h": 630, "alt": "Nova נובה: העוזרת האישית שלך לניירת"}


def social_meta(name: str) -> str:
    p, e = PAGES[name], html.escape
    url, img = SITE + p["path"], SITE + OG_IMAGE["path"]
    tags = [("property", "og:type", "website"), ("property", "og:site_name", "Nova"), ("property", "og:url", url),
            ("property", "og:title", p["title"]), ("property", "og:description", p["desc"]),
            ("property", "og:image", img), ("property", "og:image:secure_url", img), ("property", "og:image:type", "image/jpeg"),
            ("property", "og:image:width", str(OG_IMAGE["w"])), ("property", "og:image:height", str(OG_IMAGE["h"])),
            ("property", "og:image:alt", OG_IMAGE["alt"]), ("property", "og:locale", "he_IL"),
            ("property", "og:locale:alternate", "en_US"), ("name", "twitter:card", "summary_large_image"),
            ("name", "twitter:title", p["title"]), ("name", "twitter:description", p["desc"]), ("name", "twitter:image", img)]
    out = "".join(f'<meta {k}="{v}" content="{e(c)}">' for k, v, c in tags)
    return out + (f'<link rel="canonical" href="{url}">' if name != "404" else "")

# Consent first (Consent Mode v2, "advanced"): until a visitor accepts, Analytics sets no cookies and gets only
# cookieless pings; ad storage is never granted. The choice is kept in this browser (nova-consent).
def analytics_head() -> str:
    if not GA_ID:
        return ''
    return (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
            '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
            "gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500});"
            "var c=null;try{c=localStorage.getItem('nova-consent')}catch(e){}"
            "if(c==='granted')gtag('consent','update',{analytics_storage:'granted'});"
            f"gtag('js',new Date());gtag('config','{GA_ID}');</script>")

CONSENT = """<div class="consent" data-consent hidden role="dialog" aria-live="polite" aria-label="Cookies">
  <p data-l="he"><span class="consent-long">אנחנו משתמשים ב-Google Analytics כדי להבין איך משתמשים באתר. בלי פרסום, ובלי שום מידע מהאפליקציה או מהמסמכים.</span><span class="consent-short">עוגיות לסטטיסטיקה בלבד, בלי פרסום.</span> <a href="/privacy.html#site">פרטים</a></p>
  <p data-l="en"><span class="consent-long">We use Google Analytics to understand how the site is used. No ads, and nothing from the app or your documents.</span><span class="consent-short">Cookies for statistics only, no ads.</span> <a href="/privacy.html#site-en">Details</a></p>
  <div class="consent-actions">
    <button type="button" class="btn sm" data-consent-choice="granted"><span data-l="he">מאשר/ת</span><span data-l="en">Accept</span></button>
    <button type="button" class="btn alt sm" data-consent-choice="denied"><span data-l="he">לא, תודה</span><span data-l="en">No thanks</span></button>
  </div>
</div>
<script>
(function () {
  var box = document.querySelector('[data-consent]'); if (!box) return;
  var saved = null; try { saved = localStorage.getItem('nova-consent'); } catch (e) {}
  function set(open) { box.hidden = !open; document.documentElement.classList.toggle('consent-open', open); }
  // Not over the first screen: after the visitor scrolls past the hero, or after 8 seconds.
  if (!saved) {
    var hero = document.querySelector('.hero'), timer = setTimeout(show, 8000);
    function show() { clearTimeout(timer); window.removeEventListener('scroll', onScroll); if (!saved) set(true); }
    function onScroll() { if (!hero || hero.getBoundingClientRect().bottom < 0) show(); }
    window.addEventListener('scroll', onScroll, { passive: true });
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var choice = t.closest('[data-consent-choice]');
    if (choice) {
      var v = choice.getAttribute('data-consent-choice');
      try { localStorage.setItem('nova-consent', v); } catch (err) {}
      if (window.gtag) gtag('consent', 'update', { analytics_storage: v });
      saved = v; set(false); return;
    }
    if (t.closest('[data-consent-open]')) { e.preventDefault(); set(true); return; }
    if (!window.gtag) return;
    var a = t.closest('a');
    // request_access is sent by the form when a request is saved (ACCESS below), not on a click.
    if (a && /chat\\.whatsapp\\.com/.test(a.href)) gtag('event', 'join_whatsapp', { link_location: a.closest('[id]') ? a.closest('[id]').id : 'page' });
    var lang = t.closest('[data-set-lang]');
    if (lang) gtag('event', 'switch_language', { language: lang.getAttribute('data-set-lang') });
  });
})();
</script>"""

SITE_POLICY = {
    "he": """<h2 id="site">האתר hi-nova.com</h2>
      <p>באתר אנחנו משתמשים ב-Google Analytics כדי לספור ביקורים ולהבין אילו חלקים בו עוזרים, למשל כמה אנשים מבקשים להצטרף לבדיקה. Google Analytics שומר עוגיות רק אם אישרת זאת בהודעה שמופיעה באתר; אחרת הוא מקבל רק אותות בסיסיים בלי עוגיות. המידע הזה לא קשור לחשבון בנובה ולא למסמכים, ולא משמש לפרסום. אפשר לשנות את הבחירה בכל רגע דרך "הגדרות עוגיות" בתחתית האתר.</p>""",
    "en": """<h2 id="site-en">The hi-nova.com website</h2>
      <p>On the website we use Google Analytics to count visits and understand which parts help, for example how many people ask to join the test. Google Analytics sets cookies only if you accept them in the notice on the site; otherwise it receives only basic, cookieless signals. This is not linked to your Nova account or documents, and it is not used for advertising. You can change your choice at any time with "Cookie settings" at the bottom of the site.</p>""",
}

ACCESS_POLICY = {
    "he": """<h2 id="access">טופס בקשת הגישה</h2>
      <p>כדי לבקש להצטרף לבדיקה, אתם ממלאים באתר שם, כתובת Gmail (חשבון ה-Google שבטלפון), סוג הטלפון, מי אתם (למשל אדם פרטי או עורכי דין) ואיך שמעתם על נובה. אנחנו משתמשים בפרטים רק כדי לצרף אתכם לבדיקה דרך Google Play (נוסיף את הכתובת לרשימת הבודקים שם), לחזור אליכם במייל, ולדעת מאיפה מגיעים אלינו. הפרטים נשמרים במסד הנתונים של נובה (Supabase) ונשלחים לתיבת הדואר שלנו (Resend). הם לא נמכרים ולא משמשים לפרסום. נשמור אותם עד סוף תקופת הבדיקה, או עד שתבקשו למחוק אותם: {{CONTACT}}.</p>""",
    "en": """<h2 id="access-en">The request-access form</h2>
      <p>To ask to join the test, you fill in your name, your Gmail address (the Google account on your phone), your type of phone, who you are (for example a private person or a lawyer) and how you heard about Nova. We use these details only to add you to the test through Google Play (we add the address to its list of testers), to get back to you by email, and to learn how people find us. They are stored in Nova's database (Supabase) and emailed to our inbox (Resend). They are never sold or used for advertising. We keep them until the test ends, or until you ask us to delete them: {{CONTACT}}.</p>""",
}

# The request-access form (owner, 2026-11-15): a dialog opened by every "request access" button. It posts to Nova's
# API, which saves the request and emails it to Nova. Without <dialog> support or script, the button stays an email link.
def chip(name: str, value: str, he: str, en: str, required: bool = False) -> str:
    req = " required" if required else ""
    label = f'<span data-l="he">{he}</span><span data-l="en">{en}</span>' if he != en else he
    return f'<label class="chip"><input type="radio" name="{name}" value="{value}"{req}><span>{label}</span></label>'

def access_dialog() -> str:
    roles = [("individual", "אדם פרטי", "A private person"), ("lawyer", "עורך/ת דין", "Lawyer"), ("designer", "מעצב/ת פנים", "Interior designer"),
             ("architect", "אדריכל/ית", "Architect"), ("landlord", "משכיר/ה דירה", "Landlord"), ("other", "אחר", "Other")]
    sources = [("linkedin", "LinkedIn", "LinkedIn"), ("facebook", "Facebook", "Facebook"), ("instagram", "Instagram", "Instagram"),
               ("friend", "חבר/ה", "A friend"), ("other", "אחר", "Other")]
    wa = html.escape(WHATSAPP) if WHATSAPP else "#join"
    return f"""<dialog class="access" id="access-dialog" data-access aria-labelledby="access-title">
  <div class="access-body">
    <button type="button" class="access-close" data-access-close><span aria-hidden="true">×</span><span class="sr" data-l="he">סגירה</span><span class="sr" data-l="en">Close</span></button>
    <form class="access-form" data-access-form>
      <h2 id="access-title"><span data-l="he">בקשת גישה לנובה</span><span data-l="en">Request access to Nova</span></h2>
      <p class="access-lead"><span data-l="he">אנחנו פותחים מקומות בקבוצת הבודקים הראשונה, באנדרואיד. נחזור אליך במייל.</span><span data-l="en">We're opening places in the first testing group, on Android. We'll get back to you by email.</span></p>
      <label class="field"><span class="field-label"><span data-l="he">שם</span><span data-l="en">Name</span></span>
        <input type="text" name="name" required maxlength="100" autocomplete="name" autofocus></label>
      <label class="field"><span class="field-label"><span data-l="he">כתובת Gmail</span><span data-l="en">Gmail address</span></span>
        <input type="email" name="email" required maxlength="254" autocomplete="email" inputmode="email" dir="ltr">
        <span class="field-hint"><span data-l="he">Google Play מצרף בודקים לפי חשבון ה-Google שבטלפון, אז כדאי לכתוב את הכתובת הזו.</span><span data-l="en">Google Play adds testers by the Google account on their phone, so please use that address.</span></span></label>
      <fieldset class="field"><legend><span data-l="he">הטלפון שלך</span><span data-l="en">Your phone</span></legend>
        <div class="chips">{chip("phone", "android", "Android", "Android", True)}{chip("phone", "iphone", "iPhone", "iPhone")}</div>
        <p class="field-hint" data-iphone-hint hidden><span data-l="he">כרגע נובה זמינה רק באנדרואיד. ב-iPhone נכניס אותך לרשימת ההמתנה.</span><span data-l="en">Nova is Android-only for now. On iPhone, we'll put you on the waiting list.</span></p></fieldset>
      <fieldset class="field"><legend><span data-l="he">מי את/ה?</span><span data-l="en">Who are you?</span></legend>
        <div class="chips">{"".join(chip("role", v, he, en, i == 0) for i, (v, he, en) in enumerate(roles))}</div></fieldset>
      <fieldset class="field"><legend><span data-l="he">איך שמעת על נובה?</span><span data-l="en">How did you hear about Nova?</span></legend>
        <div class="chips">{"".join(chip("source", v, he, en, i == 0) for i, (v, he, en) in enumerate(sources))}</div></fieldset>
      <input class="trap" type="text" name="extra" tabindex="-1" autocomplete="off" aria-hidden="true">
      <label class="agree"><input type="checkbox" name="consent" required><span><span data-l="he">קראתי ואני מסכים/ה ל<a href="/privacy.html#access" target="_blank">מדיניות הפרטיות</a></span><span data-l="en">I agree to the <a href="/privacy.html#access-en" target="_blank">privacy policy</a></span></span></label>
      <p class="access-error" data-access-error role="alert" hidden></p>
      <button class="btn" type="submit" data-access-submit><span data-l="he">שליחה</span><span data-l="en">Send</span></button>
    </form>
    <div class="access-done" data-access-done hidden>
      <h2><span data-l="he">תודה, קיבלנו!</span><span data-l="en">Thanks, we got it!</span></h2>
      <p data-done="new" hidden><span data-l="he">נוסיף אותך לקבוצת הבודקים ונשלח הוראות התקנה לכתובת הזו.</span><span data-l="en">We'll add you to the testing group and email install instructions to this address.</span></p>
      <p data-done="waitlist" hidden><span data-l="he">נכנסת לרשימת ההמתנה. נעדכן כשנובה תגיע ל-iPhone.</span><span data-l="en">You're on the waiting list. We'll let you know when Nova comes to iPhone.</span></p>
      <p data-done="already" hidden><span data-l="he">הכתובת הזו כבר אצלנו ברשימה. נחזור אליך בקרוב.</span><span data-l="en">This address is already on our list. We'll be in touch soon.</span></p>
      <p class="access-lead"><span data-l="he">בינתיים, מוזמנים לקבוצת הבודקים בווטסאפ.</span><span data-l="en">Meanwhile, you're welcome in the testers' WhatsApp group.</span></p>
      <a class="btn" href="{wa}" target="_blank" rel="noopener">{ICONS["group"]}<span data-l="he">לקבוצת הבודקים בווטסאפ</span><span data-l="en">Join the WhatsApp group</span></a>
    </div>
  </div>
</dialog>
<script>
(function () {{
  var API = {json.dumps(API)}, CONTACT = {json.dumps(CONTACT or "")};
  var dlg = document.querySelector('[data-access]');
  if (!dlg || typeof dlg.showModal !== 'function' || !window.fetch) return;
  var form = dlg.querySelector('[data-access-form]'), done = dlg.querySelector('[data-access-done]');
  var err = dlg.querySelector('[data-access-error]'), submit = dlg.querySelector('[data-access-submit]');
  var hint = dlg.querySelector('[data-iphone-hint]'), from = 'page';
  var lang = function () {{ return document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'he'; }};
  var MSG = {{
    he: {{ bad: 'כדאי לבדוק את הפרטים ולנסות שוב.', busy: 'היו כאן הרבה בקשות. אפשר לנסות שוב בעוד שעה.', net: 'משהו השתבש. אפשר לנסות שוב, או לכתוב לנו: ' + CONTACT }},
    en: {{ bad: 'Please check the details and try again.', busy: 'There were a lot of requests from here. Please try again in an hour.', net: 'Something went wrong. Please try again, or write to us: ' + CONTACT }}
  }};
  function picked(n) {{ var c = form.querySelector('[name="' + n + '"]:checked'); return c ? c.value : ''; }}
  function field(n) {{ return form.elements.namedItem(n); }}
  function fail(kind) {{ err.textContent = MSG[lang()][kind]; err.hidden = false; }}
  function open(from_) {{
    from = from_; form.hidden = false; done.hidden = true; err.hidden = true; submit.disabled = false;
    dlg.showModal();
    if (window.gtag) gtag('event', 'access_form_open', {{ link_location: from }});
  }}
  document.addEventListener('click', function (e) {{
    var t = e.target.closest ? e.target : null; if (!t) return;
    var b = t.closest('[data-access-open]');
    if (b) {{ e.preventDefault(); open(b.closest('[id]') ? b.closest('[id]').id : 'page'); return; }}
    if (t.closest('[data-access-close]')) dlg.close();
  }});
  dlg.addEventListener('click', function (e) {{ if (e.target === dlg) dlg.close(); }});
  form.addEventListener('change', function () {{ hint.hidden = picked('phone') !== 'iphone'; }});
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    var body = {{ name: field('name').value, email: field('email').value, phone: picked('phone'), role: picked('role'),
                 source: picked('source'), lang: lang(), consent: field('consent').checked, extra: field('extra').value }};
    submit.disabled = true; err.hidden = true;
    fetch(API + '/access-requests', {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body: JSON.stringify(body) }})
      .then(function (r) {{ return r.json().catch(function () {{ return {{}}; }}).then(function (j) {{ return {{ status: r.status, body: j }}; }}); }})
      .then(function (res) {{
        submit.disabled = false;
        if (res.status !== 200 && res.status !== 201) {{ fail(res.status === 429 ? 'busy' : res.status === 400 ? 'bad' : 'net'); return; }}
        var d = (res.body && res.body.data) || {{}};
        var kind = d.alreadyListed ? 'already' : d.waitlist ? 'waitlist' : 'new';
        [].forEach.call(done.querySelectorAll('[data-done]'), function (p) {{ p.hidden = p.getAttribute('data-done') !== kind; }});
        form.hidden = true; done.hidden = false; form.reset(); hint.hidden = true;
        if (window.gtag && !d.alreadyListed) gtag('event', 'request_access', {{ role: body.role, source: body.source, phone: body.phone, link_location: from }});
      }})
      .catch(function () {{ submit.disabled = false; fail('net'); }});
  }});
}})();
</script>"""

def head(name: str, css: str, favicon_href: str) -> str:
    p = PAGES[name]
    return (f'<title>{p["title"]}</title>'
            '<meta name="claude:viewport-fit-sides" content="cover">'
            f'<meta name="description" content="{html.escape(p["desc"])}">{social_meta(name)}'
            f'<link rel="icon" href="{favicon_href}" type="image/svg+xml">'
            f'{FONTS}<style>{css}</style>{LANG_SCRIPT}')

def standalone(name: str, css: str, favicon_href: str, analytics: bool = True) -> str:
    body = fill((SRC / f"{name}.body.html").read_text(), name)
    if "data-access-open" in body:
        body += access_dialog()
    on = analytics and bool(GA_ID)
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f'{analytics_head() if on else ""}{head(name, css, favicon_href)}</head><body>{body}{CONSENT if on else ""}</body></html>\n')

def main() -> None:
    css = (SRC / "style.css").read_text()
    site, preview = ROOT / "docs", ROOT / "preview"
    site.mkdir(exist_ok=True); preview.mkdir(exist_ok=True)
    for name in PAGES:
        (site / f"{name}.html").write_text(standalone(name, css, "/favicon.svg" if name == "404" else "favicon.svg"))
    # Android trusts that hi-nova.com and the app belong together: invite links open the app, and passkeys work.
    wk = site / ".well-known"; wk.mkdir(exist_ok=True)
    (wk / "assetlinks.json").write_text(json.dumps([{
        "relation": ["delegate_permission/common.handle_all_urls", "delegate_permission/common.get_login_creds"],
        "target": {"namespace": "android_app", "package_name": "com.hinova.app", "sha256_cert_fingerprints": SIGNING_CERTS},
    }], indent=2) + "\n")
    (site / "favicon.svg").write_text(FAVICON)
    (site / "og.jpg").write_bytes((SRC / "og.jpg").read_bytes())  # the link-preview card
    # The app's screens (sample data), for the gallery.
    for d in (site / "img", preview / "img"):
        d.mkdir(parents=True, exist_ok=True)
        for f in (SRC / "img").glob("*.png"):
            (d / f.name).write_bytes(f.read_bytes())
    (site / ".nojekyll").write_text("")          # GitHub Pages: serve /.well-known as is
    (site / "CNAME").write_text("hi-nova.com\n")
    # The preview: the landing page as the Artifact's page (no document shell), the policy as a full page beside it.
    favicon_data = "data:image/svg+xml," + FAVICON.replace("#", "%23").replace('"', "'")
    body = fill((SRC / "index.body.html").read_text(), "index") + access_dialog()
    (preview / "index.html").write_text(head("index", css, favicon_data) + body + "\n")
    (preview / "privacy.html").write_text(standalone("privacy", css, favicon_data, analytics=False))
    print("built", sorted(str(p.relative_to(ROOT)) for p in site.iterdir()), sorted(str(p.relative_to(ROOT)) for p in preview.iterdir()))

main()
