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
SIGNING_CERTS = ["75:89:65:B2:6A:42:CF:59:F4:B9:E7:99:EB:9B:54:D6:38:2F:83:24:17:6D:CF:08:AC:1A:D2:A6:3C:A3:32:9D"]
# Google Analytics 4 (owner, 2026-11-15). Empty: no analytics anywhere, and the policy says nothing about it.
GA_ID = os.environ.get("NOVA_GA_ID", "")
WHATSAPP = os.environ.get("NOVA_WHATSAPP", "https://chat.whatsapp.com/GicdUQKgHyyL1c5hftEtMw")  # the testers' WhatsApp group (owner, 2026-11-14)

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

def cta(small: bool = False) -> str:
    sm = " sm" if small else ""
    wa = html.escape(WHATSAPP) if WHATSAPP else "#join"
    subject = "%D7%91%D7%A7%D7%A9%D7%94%20%D7%9C%D7%A0%D7%A1%D7%95%D7%AA%20%D7%90%D7%AA%20%D7%A0%D7%95%D7%91%D7%94"  # "בקשה לנסות את נובה"
    mail = f"mailto:{html.escape(CONTACT) if CONTACT else 'contact@hi-nova.com'}?subject={subject}"
    return (f'<a class="btn{sm}" href="{wa}" target="_blank" rel="noopener">{ICONS["group"]}'
            '<span data-l="he">לקבוצת הבודקים בווטסאפ</span><span data-l="en">Join the WhatsApp group</span></a>'
            f'<a class="btn alt{sm}" href="{mail}">{ICONS["mail"]}'
            '<span data-l="he">לבקש גישה לנובה</span><span data-l="en">Request access</span></a>')

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
               .replace("{{CTA_BUTTONS_SMALL}}", cta(small=True)).replace("{{CTA_BUTTONS}}", cta())
               .replace("{{CHAT_SCRIPT}}", CHAT_SCRIPT % json.dumps(CHAT, ensure_ascii=False))
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

PAGES = {
    "index": {"title": "Nova", "desc": "נובה, העוזרת האישית שלך לניירת. Nova, your personal paperwork assistant."},
    "privacy": {"title": "Nova Privacy Policy", "desc": "מדיניות הפרטיות של נובה. Nova's privacy policy."},
    "404": {"title": "Nova", "desc": "נובה, העוזרת האישית שלך לניירת. Nova, your personal paperwork assistant."},
}

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
  <p data-l="he">אנחנו משתמשים ב-Google Analytics כדי להבין איך משתמשים באתר. בלי פרסום, ובלי שום מידע מהאפליקציה או מהמסמכים. <a href="/privacy.html#site">פרטים</a></p>
  <p data-l="en">We use Google Analytics to understand how the site is used. No ads, and nothing from the app or your documents. <a href="/privacy.html#site">Details</a></p>
  <div class="consent-actions">
    <button type="button" class="btn sm" data-consent-choice="granted"><span data-l="he">מאשר/ת</span><span data-l="en">Accept</span></button>
    <button type="button" class="btn alt sm" data-consent-choice="denied"><span data-l="he">לא, תודה</span><span data-l="en">No thanks</span></button>
  </div>
</div>
<script>
(function () {
  var box = document.querySelector('[data-consent]'); if (!box) return;
  var saved = null; try { saved = localStorage.getItem('nova-consent'); } catch (e) {}
  if (!saved) box.hidden = false;
  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : null; if (!t) return;
    var choice = t.closest('[data-consent-choice]');
    if (choice) {
      var v = choice.getAttribute('data-consent-choice');
      try { localStorage.setItem('nova-consent', v); } catch (err) {}
      if (window.gtag) gtag('consent', 'update', { analytics_storage: v });
      box.hidden = true; return;
    }
    if (t.closest('[data-consent-open]')) { e.preventDefault(); box.hidden = false; return; }
    if (!window.gtag) return;
    var a = t.closest('a');
    if (a && /chat\\.whatsapp\\.com/.test(a.href)) gtag('event', 'join_whatsapp', { link_location: a.closest('[id]') ? a.closest('[id]').id : 'page' });
    else if (a && /^mailto:/.test(a.getAttribute('href') || '')) gtag('event', 'request_access', { link_location: a.closest('[id]') ? a.closest('[id]').id : 'page' });
    var lang = t.closest('[data-set-lang]');
    if (lang) gtag('event', 'switch_language', { language: lang.getAttribute('data-set-lang') });
  });
})();
</script>"""

SITE_POLICY = {
    "he": """<h2 id="site">האתר hi-nova.com</h2>
      <p>באתר אנחנו משתמשים ב-Google Analytics כדי לספור ביקורים ולהבין אילו חלקים בו עוזרים, למשל כמה אנשים מבקשים להצטרף לבדיקה. Google Analytics שומר עוגיות רק אם אישרת זאת בהודעה שמופיעה באתר; אחרת הוא מקבל רק אותות בסיסיים בלי עוגיות. המידע הזה לא קשור לחשבון בנובה ולא למסמכים, ולא משמש לפרסום. אפשר לשנות את הבחירה בכל רגע דרך "הגדרות עוגיות" בתחתית האתר.</p>""",
    "en": """<h2 id="site">The hi-nova.com website</h2>
      <p>On the website we use Google Analytics to count visits and understand which parts help, for example how many people ask to join the test. Google Analytics sets cookies only if you accept them in the notice on the site; otherwise it receives only basic, cookieless signals. This is not linked to your Nova account or documents, and it is not used for advertising. You can change your choice at any time with "Cookie settings" at the bottom of the site.</p>""",
}

def head(name: str, css: str, favicon_href: str) -> str:
    p = PAGES[name]
    return (f'<title>{p["title"]}</title>'
            '<meta name="claude:viewport-fit-sides" content="cover">'
            f'<meta name="description" content="{html.escape(p["desc"])}">'
            f'<link rel="icon" href="{favicon_href}" type="image/svg+xml">'
            f'{FONTS}<style>{css}</style>{LANG_SCRIPT}')

def standalone(name: str, css: str, favicon_href: str, analytics: bool = True) -> str:
    body = fill((SRC / f"{name}.body.html").read_text(), name)
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
    # The app's screens (sample data), for the gallery.
    for d in (site / "img", preview / "img"):
        d.mkdir(parents=True, exist_ok=True)
        for f in (SRC / "img").glob("*.png"):
            (d / f.name).write_bytes(f.read_bytes())
    (site / ".nojekyll").write_text("")          # GitHub Pages: serve /.well-known as is
    (site / "CNAME").write_text("hi-nova.com\n")
    # The preview: the landing page as the Artifact's page (no document shell), the policy as a full page beside it.
    favicon_data = "data:image/svg+xml," + FAVICON.replace("#", "%23").replace('"', "'")
    body = fill((SRC / "index.body.html").read_text(), "index")
    (preview / "index.html").write_text(head("index", css, favicon_data) + body + "\n")
    (preview / "privacy.html").write_text(standalone("privacy", css, favicon_data, analytics=False))
    print("built", sorted(str(p.relative_to(ROOT)) for p in site.iterdir()), sorted(str(p.relative_to(ROOT)) for p in preview.iterdir()))

main()
