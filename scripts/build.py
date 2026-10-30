"""Builds the profile README and its live SVG cards from public GitHub data.
Runs in GitHub Actions on a schedule; safe to run locally."""
import json, os, urllib.request, datetime as dt, html, pathlib

USER = "Adi-1626"
ROOT = pathlib.Path(__file__).resolve().parent.parent
A = ROOT / "assets"; A.mkdir(exist_ok=True)
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NOW = dt.datetime.now(dt.timezone.utc)

FEATURED = [  # repo, display name, tagline, link
    ("Haven", "Haven", "Text channels, voice rooms and screen sharing in one calm place for your people.", "https://haven-landing.pages.dev/"),
    ("OmniChat", "OmniChat", "AI chat CLI with real-time streaming and a live tokens-per-second meter, on Cerebras.", "https://github.com/Adi-1626/OmniChat"),
    ("AntiClickbait", "Clickbait Clarifier", "Flags misleading YouTube videos with an ML and LLM ensemble, right in the browser.", "https://github.com/Adi-1626/AntiClickbait"),
    ("VendorVault", "VendorVault", "Point-of-sale desktop app with barcode scanning, billing, stock and sales analytics.", "https://github.com/Adi-1626/VendorVault"),
]
LANG = {"TypeScript": "#3178c6", "Python": "#3572A5", "JavaScript": "#f1e05a", "Kotlin": "#A97BFF", "Java": "#b07219"}

THEMES = {
    "dark":  dict(bg="#0d1117", card="#111318", border="#262a33", text="#f0f2f5", muted="#8b929c", faint="#5c636e", accent="#a78bfa", glow="#7c3aed"),
    "light": dict(bg="#ffffff", card="#ffffff", border="#e4e6eb", text="#0b0d12", muted="#5b616b", faint="#9aa0a8", accent="#6d28d9", glow="#a78bfa"),
}
SANS = "font-family:Inter,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Consolas,monospace"

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok: req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def ago(iso):
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")); s = (NOW - t).total_seconds()
    for unit, n in (("year", 31536000), ("month", 2592000), ("week", 604800), ("day", 86400), ("hour", 3600), ("min", 60)):
        if s >= n: k = int(s // n); return f"{k} {unit}{'s' if k > 1 and unit != 'min' else ''} ago"
    return "just now"

def esc(s): return html.escape(s or "", quote=True)

def wrap(text, n):
    out, line = [], ""
    for w in text.split():
        if len(line) + len(w) + 1 > n: out.append(line); line = w
        else: line = f"{line} {w}".strip()
    return out + [line]

# ---------- data ----------
repos = {r["name"]: r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")}
events = get(f"https://api.github.com/users/{USER}/events/public?per_page=100")
user = get(f"https://api.github.com/users/{USER}")

# commits in last 30 days per featured repo (public)
since = (NOW - dt.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
def commits30(repo):
    try: return len(get(f"https://api.github.com/repos/{USER}/{repo}/commits?since={since}&per_page=100"))
    except Exception: return 0

# ---------- header ----------
pub = [r for r in repos.values() if not r.get("private") and not r.get("fork") and r.get("pushed_at") and r["name"] != USER]
top = max(pub, key=lambda r: r["pushed_at"], default=None)
status = f"Active now · last commit {ago(top['pushed_at'])}" if top else "Open to opportunities"
for name, c in THEMES.items():
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300">
<style>.p{{animation:p 2.4s ease-in-out infinite}}@keyframes p{{50%{{opacity:.25}}}}
.f{{opacity:0;animation:f .9s cubic-bezier(.2,.7,.2,1) forwards}}@keyframes f{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.s{{animation:s 9s ease-in-out infinite alternate}}@keyframes s{{to{{transform:translateX(-40px)}}}}</style>
<defs><radialGradient id="g" cx=".82" cy=".35" r=".55"><stop offset="0" stop-color="{c['glow']}" stop-opacity="{'.32' if name=='dark' else '.18'}"/><stop offset="1" stop-color="{c['glow']}" stop-opacity="0"/></radialGradient>
<pattern id="d" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{c['border']}"/></pattern>
<linearGradient id="fade" x1="0" x2="1"><stop offset=".35" stop-color="{c['bg']}"/><stop offset="1" stop-color="{c['bg']}" stop-opacity="0"/></linearGradient>
<clipPath id="r"><rect width="1200" height="300" rx="20"/></clipPath></defs>
<g clip-path="url(#r)"><rect width="1200" height="300" fill="{c['bg']}"/><rect width="1200" height="300" fill="url(#d)"/><rect width="1200" height="300" fill="url(#fade)"/>
<g class="s"><rect width="1300" height="300" fill="url(#g)"/></g></g>
<rect x=".5" y=".5" width="1199" height="299" rx="20" fill="none" stroke="{c['border']}"/>
<g class="f" style="animation-delay:.05s"><text x="64" y="92" font-size="14" fill="{c['muted']}" letter-spacing="2.5" style="{MONO}">PUNE, INDIA · FULL STACK &amp; AI</text></g>
<g class="f" style="animation-delay:.15s"><text x="62" y="160" font-size="58" font-weight="700" fill="{c['text']}" letter-spacing="-1.8" style="{SANS}">Aditya Gawali</text></g>
<g class="f" style="animation-delay:.25s"><text x="64" y="200" font-size="20" fill="{c['muted']}" style="{SANS}">I build real-time products and the AI and cloud systems behind them.</text></g>
<g class="f" style="animation-delay:.35s"><rect x="64" y="226" width="{len(status)*7.4+44:.0f}" height="32" rx="16" fill="{c['card']}" stroke="{c['border']}"/>
<circle cx="84" cy="242" r="4.5" fill="#22c55e" class="p"/><text x="98" y="247" font-size="13" fill="{c['text']}" style="{MONO}">{esc(status)}</text></g>
</svg>'''
    (A / f"header-{name}.svg").write_text(svg)

# ---------- project cards ----------
for repo, title, tag, link in FEATURED:
    r = repos.get(repo, {}); lang = r.get("language") or "—"; stars = r.get("stargazers_count", 0)
    upd = ago(r["pushed_at"]) if r.get("pushed_at") else ""; n30 = commits30(repo)
    live = n30 > 0
    for name, c in THEMES.items():
        lines = "".join(f'<text x="28" y="{86+i*22}" font-size="14.5" fill="{c["muted"]}" style="{SANS}">{esc(l)}</text>' for i, l in enumerate(wrap(tag, 58)[:2]))
        lbl = f'{n30} commit{"s" if n30 != 1 else ""} · 30d'; bw = len(lbl) * 7.1 + 34; bx = 532 - bw
        badge = (f'<rect x="{bx:.0f}" y="26" width="{bw:.0f}" height="24" rx="12" fill="#22c55e" fill-opacity=".12"/><circle cx="{bx+14:.0f}" cy="38" r="3.5" fill="#22c55e" class="p"/>'
                 f'<text x="{bx+24:.0f}" y="42" font-size="11.5" fill="#22c55e" style="{MONO}">{lbl}</text>') if live else ""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="560" height="180" viewBox="0 0 560 180">
<style>.p{{animation:p 2.4s ease-in-out infinite}}@keyframes p{{50%{{opacity:.25}}}}</style>
<rect x=".5" y=".5" width="559" height="179" rx="16" fill="{c['card']}" stroke="{c['border']}"/>
<text x="28" y="48" font-size="21" font-weight="650" fill="{c['text']}" letter-spacing="-.4" style="{SANS}">{esc(title)}</text>
{badge}{lines}
<line x1="28" y1="136" x2="532" y2="136" stroke="{c['border']}"/>
<circle cx="34" cy="157" r="5" fill="{LANG.get(lang, c['faint'])}"/><text x="46" y="161" font-size="12.5" fill="{c['muted']}" style="{MONO}">{esc(lang)}</text>
{f'<text x="170" y="161" font-size="12.5" fill="{c["muted"]}" style="{MONO}">★ {stars}</text>' if stars else ""}
<text x="532" y="161" font-size="12.5" fill="{c['faint']}" text-anchor="end" style="{MONO}">updated {esc(upd)}</text>
</svg>'''
        (A / f"card-{repo.lower()}-{name}.svg").write_text(svg)

# ---------- recent activity ----------
acts, seen = [], set()
for e in events:
    repo = e["repo"]["name"].split("/")[1]; t = e["type"]; p = e.get("payload", {})
    if t == "PullRequestEvent" and p.get("action") in ("opened", "merged", "closed"):
        num = p.get("number") or p.get("pull_request", {}).get("number")
        if ("pr", repo, num) in seen: continue
        try: pr = get(f"https://api.github.com/repos/{USER}/{repo}/pulls/{num}")
        except Exception: continue
        seen.add(("pr", repo, num))
        verb = "Merged" if pr.get("merged_at") else ("Opened" if pr.get("state") == "open" else "Closed")
        acts.append(f"{verb} [{esc(pr.get('title'))}]({pr.get('html_url')}) in **{repo}** · {ago(e['created_at'])}")
    elif t == "ReleaseEvent":
        rel = p.get("release", {}); acts.append(f"Released [{esc(rel.get('tag_name'))}]({rel.get('html_url')}) of **{repo}** · {ago(e['created_at'])}")
    elif t == "PushEvent":
        k = ("push", repo)
        if k in seen: continue
        seen.add(k); acts.append(f"Pushed to **[{repo}](https://github.com/{USER}/{repo})** · {ago(e['created_at'])}")
    elif t == "CreateEvent" and p.get("ref_type") == "repository":
        acts.append(f"Created **[{repo}](https://github.com/{USER}/{repo})** · {ago(e['created_at'])}")
    if len(acts) >= 5: break
activity = "\n".join(f"- {a}" for a in acts) or "- Quiet week. Probably reading docs."
VER = NOW.strftime("%Y%m%d%H%M")
synced = NOW.astimezone(IST).strftime("%d %b %Y, %H:%M IST")

# ---------- README ----------
def pic(base, alt, href, width):
    return (f'<a href="{href}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/{base}-dark.svg?v={VER}">'
            f'<img src="assets/{base}-light.svg?v={VER}" width="{width}" alt="{esc(alt)}"></picture></a>')
cards = [pic(f"card-{r.lower()}", t, l, "49%") for r, t, _, l in FEATURED]
readme = f'''{pic("header", "Aditya Gawali — Full Stack & AI Engineer", "https://haven-landing.pages.dev/", "100%")}

<p>
<a href="https://portfolio-nu-cyan-5mpw4wfqg1.vercel.app/"><b>Portfolio</b></a> &nbsp;·&nbsp;
<a href="https://www.linkedin.com/in/aditya-gawali-b13a50265/"><b>LinkedIn</b></a> &nbsp;·&nbsp;
<a href="https://portfolio-nu-cyan-5mpw4wfqg1.vercel.app/resume.pdf"><b>Résumé</b></a> &nbsp;·&nbsp;
<a href="mailto:adityagawali16@gmail.com"><b>Email</b></a>
</p>

Full Stack &amp; AI Intern at **Sectfit Healthtech**, working across frontend, backend, AI integrations and cloud. Computer Engineering at NBN Sinhgad, Pune, class of 2027. Previously AWS intern at Sanyu Infotech and Android intern at Infeanet.

### Selected work

{cards[0]}&nbsp;{cards[1]}
{cards[2]}&nbsp;{cards[3]}

<details>
<summary><b>Haven, in one screen</b></summary>
<br>
<a href="https://haven-landing.pages.dev/"><img src="https://raw.githubusercontent.com/Adi-1626/Haven/main/docs/screenshots/Haven-landing.jpg" width="100%" alt="Haven landing page"></a>
</details>

### Recently

{activity}

### Toolkit

`TypeScript` `Python` `Node.js` `React` `Next.js` `WebRTC` `Supabase` `AWS` `Docker` `Cloudflare` `LLM integrations` `scikit-learn`

<sub>Cards and activity refresh from GitHub every 6 hours · last synced {synced}</sub>
'''
(ROOT / "README.md").write_text(readme)
print("built", synced)
