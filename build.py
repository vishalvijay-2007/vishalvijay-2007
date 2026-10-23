#!/usr/bin/env python3
"""
Builds a dark-maroon "editorial" GitHub profile README.

Reads  : profile.json  (your details)  +  assets/photo.jpg (optional photo)
Writes : README.md  +  assets/*.svg

No extra libraries needed - only Python 3.8+.
If GITHUB_TOKEN is set (GitHub Actions does this for you) the commit
heat-map and stats use your REAL GitHub activity. Otherwise sample data is used.
"""
import base64, datetime, html, json, os, random, textwrap, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

# ------------------------------------------------------------------ theme
BG, CREAM, MUTED = "#0b0610", "#f5e9ee", "#b98aa2"
PINK, CRIMSON, LINE = "#ff3d7f", "#c2185b", "#7a2250"
SERIF = "Georgia,'Iowan Old Style','Times New Roman',serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W = 900  # every banner is 900 px wide and scales to 100% in the README

HEAT = ["#2a1022", "#5c1236", "#8f1b4d", "#c2185b", "#ff3d7f"]


def esc(s):
    return html.escape(str(s), quote=True)


def wrap(text, size, maxw, factor=0.52):
    n = max(8, int(maxw / (size * factor)))
    return textwrap.wrap(str(text), n) or [""]


def svg_doc(w, h, body, extra_defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<defs>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a0f27"/><stop offset="1" stop-color="#140813"/></linearGradient>
<linearGradient id="hero" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6e1442"/><stop offset=".55" stop-color="#2c0c1f"/><stop offset="1" stop-color="#0d0710"/></linearGradient>
<linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{PINK}"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></linearGradient>
<radialGradient id="glow" cx=".8" cy=".35" r=".7"><stop offset="0" stop-color="{PINK}" stop-opacity=".35"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
{extra_defs}
</defs>
<style>
.serif{{font-family:{SERIF}}} .mono{{font-family:{MONO}}}
.blink{{animation:b 1.1s steps(2,start) infinite}} @keyframes b{{to{{visibility:hidden}}}}
</style>
{body}
</svg>"""


def save(name, content):
    with open(os.path.join(ASSETS, name), "w", encoding="utf-8") as f:
        f.write(content)


def brackets(x, y, w, h, n=14, color=PINK, op=0.9):
    d = (f"M{x},{y+n} V{y} H{x+n} M{x+w-n},{y} H{x+w} V{y+n} "
         f"M{x+w},{y+h-n} V{y+h} H{x+w-n} M{x+n},{y+h} H{x} V{y+h-n}")
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.6" opacity="{op}"/>'


def card(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#card)" '
            f'stroke="{LINE}" stroke-opacity=".8"/>' + brackets(x + 6, y + 6, w - 12, h - 12))


def number_word(n):
    words = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen "
             "Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty").split()
    return words[n] if 0 <= n < len(words) else str(n)


# ------------------------------------------------------------------ pieces
def heading(num, label, title, right=""):
    right_txt = (f'<text x="{W}" y="26" text-anchor="end" class="mono" font-size="10" '
                 f'letter-spacing="2" fill="{MUTED}">{esc(right)}</text>') if right else ""
    body = f"""
<text x="0" y="26" class="mono" font-size="11" letter-spacing="3" fill="{PINK}">{num:02d} · {esc(label.upper())}</text>
{right_txt}
<text x="0" y="74" class="serif" font-size="38" font-weight="700" fill="{CREAM}">{esc(title)}</text>
<rect x="0" y="92" width="{W}" height="1.5" fill="url(#rule)"/>"""
    return svg_doc(W, 104, body)


def hero(p, photo_b64):
    words = p["name"].split()
    if len(words) >= 2:
        l1, l2 = " ".join(words[:-1]), words[-1] + "."
    else:
        l1, l2 = "", words[0] + "."
    y = 150
    name_svg = ""
    if l1:
        name_svg += f'<text x="48" y="{y}" class="serif" font-size="70" font-weight="700" fill="{CREAM}">{esc(l1)}</text>'
        y += 76
    name_svg += (f'<text x="48" y="{y}" class="serif" font-size="70" font-style="italic" '
                 f'font-weight="700" fill="{CREAM}">{esc(l2)}</text>')
    roles = "  ·  ".join(p.get("roles", []))
    tags = "  ·  ".join(p.get("hero_tags", []))
    arch = ("M650,330 V150 A100,100 0 0 1 850,150 V330 Z")
    if photo_b64:
        photo = (f'<image href="data:image/jpeg;base64,{photo_b64}" x="650" y="50" width="200" '
                 f'height="280" preserveAspectRatio="xMidYMid slice" clip-path="url(#arch)"/>')
    else:
        initials = "".join(w[0] for w in words[:2]).upper()
        photo = (f'<rect x="650" y="50" width="200" height="280" fill="#3a0f27" clip-path="url(#arch)"/>'
                 f'<text x="750" y="215" text-anchor="middle" class="serif" font-size="80" '
                 f'font-style="italic" fill="{PINK}">{esc(initials)}</text>')
    body = f"""
<rect width="{W}" height="400" rx="20" fill="url(#hero)" stroke="{LINE}"/>
<rect width="{W}" height="400" rx="20" fill="url(#glow)"/>
{brackets(14, 14, W-28, 372, 22)}
<text x="48" y="64" class="mono" font-size="11" letter-spacing="3" fill="{PINK}">{esc(roles.upper())}</text>
{name_svg}
<text x="48" y="{y+44}" class="serif" font-size="22" font-style="italic" fill="{MUTED}">{esc(p.get("tagline",""))}</text>
<text x="48" y="372" class="mono" font-size="10.5" letter-spacing="1.5" fill="{MUTED}">{esc(tags.upper())}</text>
<path d="{arch}" fill="none" stroke="{PINK}" stroke-width="1.5" transform="translate(-6,-6) scale(1.0)" opacity=".5"/>
{photo}
<path d="{arch}" fill="none" stroke="{PINK}" stroke-width="2"/>
<circle cx="850" cy="369" r="4" fill="{PINK}"><animate attributeName="opacity" values="1;.2;1" dur="2s" repeatCount="indefinite"/></circle>
<text x="838" y="372" text-anchor="end" class="mono" font-size="9" letter-spacing="2" fill="{MUTED}">{esc(p.get("status","OPEN TO WORK").upper())}</text>"""
    defs = f'<clipPath id="arch"><path d="{arch}"/></clipPath>'
    return svg_doc(W, 400, body, defs)


def chip(label, value):
    lw = int(len(label) * 7.2 + 24)
    vw = int(len(value) * 7.4 + 26)
    w = lw + vw
    body = f"""
<rect width="{lw+6}" height="32" rx="6" fill="#1a0b17" stroke="{LINE}"/>
<rect x="{lw}" width="{vw}" height="32" rx="6" fill="{CRIMSON}"/>
<text x="{lw/2:.0f}" y="21" text-anchor="middle" class="mono" font-size="11" letter-spacing="1.5" fill="{MUTED}">{esc(label.upper())}</text>
<text x="{lw+vw/2:.0f}" y="21" text-anchor="middle" class="mono" font-size="11.5" font-weight="700" fill="#fff">{esc(value.upper())}</text>"""
    return w, svg_doc(w, 32, body)


def about(p):
    lines = p.get("terminal", [])
    h = max(300, 84 + 26 * len(lines))
    handle = p.get("github_username", "me").lower()
    tl = ""
    y = 86
    for ln in lines:
        if ln.startswith("$"):
            tl += (f'<text x="42" y="{y}" class="mono" font-size="13" font-weight="700" fill="{PINK}">$</text>'
                   f'<text x="58" y="{y}" class="mono" font-size="13" font-weight="700" fill="{CREAM}">{esc(ln[1:].strip())}</text>')
        else:
            tl += f'<text x="58" y="{y}" class="mono" font-size="13" fill="{MUTED}">{esc(ln)}</text>'
        y += 26
    tl += f'<rect x="58" y="{y-13}" width="9" height="15" fill="{PINK}" class="blink"/>'
    side = ""
    cards = p.get("about_cards", [])[:3]
    ch = (h - 14 * (len(cards) - 1)) / max(1, len(cards))
    for i, c in enumerate(cards):
        cy = i * (ch + 14)
        side += card(600, cy, 300, ch)
        side += (f'<text x="620" y="{cy+28}" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">{esc(c["label"].upper())}</text>'
                 f'<text x="620" y="{cy+ch/2+12:.0f}" class="serif" font-size="28" font-weight="700" fill="{CREAM}">{esc(c["value"])}</text>'
                 f'<text x="620" y="{cy+ch-18:.0f}" class="mono" font-size="10.5" fill="{MUTED}">{esc(c.get("note",""))}</text>')
    body = f"""
<rect x="0" y="0" width="576" height="{h}" rx="14" fill="#10070f" stroke="{LINE}"/>
<rect x="0" y="0" width="576" height="38" rx="14" fill="#25091a"/><rect x="0" y="24" width="576" height="14" fill="#25091a"/>
<circle cx="22" cy="19" r="5" fill="#ff5f7e"/><circle cx="40" cy="19" r="5" fill="#ffbd5a"/><circle cx="58" cy="19" r="5" fill="#7be0a4"/>
<text x="288" y="23" text-anchor="middle" class="mono" font-size="11" fill="{MUTED}">{esc(handle)}@portfolio ~</text>
{tl}
{side}"""
    return svg_doc(W, h, body)


def skills(p):
    items = p.get("skills", [])
    cw, gap, ch = 286, 21, 160
    rows = (len(items) + 2) // 3
    body = ""
    for i, s in enumerate(items):
        x, y = (i % 3) * (cw + gap), (i // 3) * (ch + gap)
        body += card(x, y, cw, ch)
        body += f'<text x="{x+22}" y="{y+32}" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">{i+1:02d} · {esc(s["label"].upper())}</text>'
        ty = y + 66
        for j, line in enumerate(s["lines"][:3]):
            size = 21 if j == 0 else (16 if j == 1 else 13)
            wgt = 700 if j < 2 else 400
            body += f'<text x="{x+22}" y="{ty}" class="serif" font-size="{size}" font-weight="{wgt}" fill="{CREAM if j<2 else MUTED}">{esc(line)}</text>'
            ty += size + 9
        if s.get("footer"):
            body += f'<text x="{x+22}" y="{y+ch-18}" class="mono" font-size="9" letter-spacing="1.5" fill="{MUTED}">{esc(s["footer"].upper())}</text>'
    return svg_doc(W, rows * (ch + gap) - gap, body)


# ------------------------------------------------------------------ github data
def fetch_github(login, token):
    q = """query($login:String!){user(login:$login){
      contributionsCollection{totalCommitContributions
        contributionCalendar{totalContributions weeks{contributionDays{contributionCount date}}}}
      pullRequests{totalCount} issues{totalCount}
      repositoriesContributedTo(first:1,contributionTypes:[COMMIT,ISSUE,PULL_REQUEST,REPOSITORY]){totalCount}
      repositories(ownerAffiliations:OWNER,first:100,isFork:false){nodes{stargazerCount}}}}"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": q, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-readme-builder"})
    u = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]
    cc = u["contributionsCollection"]
    weeks = [[d["contributionCount"] for d in w["contributionDays"]]
             for w in cc["contributionCalendar"]["weeks"]]
    dates = [[d["date"] for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    return {
        "weeks": weeks, "dates": dates, "real": True,
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": u["pullRequests"]["totalCount"], "issues": u["issues"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
    }


def sample_github():
    rnd = random.Random(7)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday() + 1 + 52 * 7)
    weeks, dates = [], []
    for w in range(53):
        wk, dt = [], []
        for d in range(7):
            day = start + datetime.timedelta(days=w * 7 + d)
            dt.append(day.isoformat())
            wk.append(0 if day > today else (rnd.choice([0, 0, 1, 2, 4, 7]) if w > 20 else rnd.choice([0, 0, 0, 1])))
        weeks.append(wk)
        dates.append(dt)
    total = sum(map(sum, weeks))
    return {"weeks": weeks, "dates": dates, "real": False, "total": total, "commits": int(total * .8),
            "prs": 12, "issues": 4, "contributed": 6, "stars": 9}


def streak(weeks):
    days = [c for w in weeks for c in w]
    best = cur = 0
    for c in days:
        cur = cur + 1 if c > 0 else 0
        best = max(best, cur)
    return best


def commit_log(g):
    weeks = g["weeks"]
    flat = [c for w in weeks for c in w]
    mx = max(flat) or 1
    active = sum(1 for c in flat if c > 0)
    cell, gap, ox, oy = 12, 3, 44, 168
    body = card(0, 0, W, 360)
    label = "REAL GITHUB ACTIVITY" if g["real"] else "SAMPLE DATA - REAL DATA AFTER SETUP"
    body += f'<text x="30" y="36" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">COMMIT LOG · {label}</text>'
    body += (f'<text x="30" y="82" class="serif" font-size="26" font-weight="700" fill="{CREAM}">A year of building, '
             f'<tspan font-style="italic" fill="{PINK}">one square at a time.</tspan></text>')
    stats = [(f'{g["total"]:,}', "CONTRIBUTIONS"), (str(active), "ACTIVE DAYS"), (str(streak(weeks)), "LONGEST STREAK")]
    for i, (v, l) in enumerate(stats):
        sx = 560 + i * 110
        body += (f'<text x="{sx}" y="62" class="serif" font-size="30" font-weight="700" fill="{CREAM}">{v}</text>'
                 f'<text x="{sx}" y="80" class="mono" font-size="8.5" letter-spacing="1.5" fill="{MUTED}">{l}</text>')
    # month labels + grid
    last_m, last_wi = None, -10
    for wi, wk in enumerate(weeks):
        m = datetime.date.fromisoformat(g["dates"][wi][0]).strftime("%b")
        if m != last_m and wi - last_wi >= 3:
            last_wi = wi
            body += f'<text x="{ox+wi*(cell+gap)}" y="{oy-10}" class="mono" font-size="9" fill="{MUTED}">{m}</text>'
        last_m = m
        for di, c in enumerate(wk):
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
            body += f'<rect x="{ox+wi*(cell+gap)}" y="{oy+di*(cell+gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{HEAT[lvl]}"/>'
    for di, n in ((0, "Mon"), (2, "Wed"), (4, "Fri")):
        body += f'<text x="30" y="{oy+(di+1)*(cell+gap)-5}" text-anchor="end" class="mono" font-size="9" fill="{MUTED}">{n}</text>'
    # legend
    lx = W - 30 - 5 * 17 - 70
    body += f'<text x="{lx}" y="{oy+7*(cell+gap)+16}" class="mono" font-size="9" fill="{MUTED}">Less</text>'
    for i, col in enumerate(HEAT):
        body += f'<rect x="{lx+34+i*17}" y="{oy+7*(cell+gap)+7}" width="12" height="12" rx="2.5" fill="{col}"/>'
    body += f'<text x="{lx+34+5*17+4}" y="{oy+7*(cell+gap)+16}" class="mono" font-size="9" fill="{MUTED}">More</text>'
    # totals row
    tot = [("Total stars earned", g["stars"]), ("Total commits (past year)", g["commits"]),
           ("Total PRs", g["prs"]), ("Total issues", g["issues"]), ("Contributed to (past year)", g["contributed"])]
    for i, (l, v) in enumerate(tot):
        tx = 30 + i * 172
        body += (f'<text x="{tx}" y="{oy+7*(cell+gap)+58}" class="serif" font-size="22" font-weight="700" fill="{CREAM}">{v}</text>'
                 f'<text x="{tx}" y="{oy+7*(cell+gap)+74}" class="mono" font-size="8.5" letter-spacing="1" fill="{MUTED}">{esc(l.upper())}</text>')
    return svg_doc(W, 360, body)


def achievements(p):
    items = p.get("achievements", [])[:6]
    cw, gap, ch = 286, 21, 150
    rows = (len(items) + 2) // 3
    body = ""
    for i, a in enumerate(items):
        x, y = (i % 3) * (cw + gap), (i // 3) * (ch + gap)
        body += card(x, y, cw, ch)
        body += (f'<text x="{x+22}" y="{y+32}" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">{esc(a["org"].upper())}</text>'
                 f'<text x="{x+22}" y="{y+82}" class="serif" font-size="{min(38, int(242 / (len(a["headline"]) * 0.54)))}" font-weight="700" fill="{CREAM}">{esc(a["headline"])}</text>')
        for j, ln in enumerate(wrap(a.get("detail", ""), 14, cw - 44)[:2]):
            body += f'<text x="{x+22}" y="{y+112+j*18}" class="serif" font-size="14" font-style="italic" fill="{MUTED}">{esc(ln)}</text>'
    return svg_doc(W, rows * (ch + gap) - gap, body)


def project(i, pr):
    h = 220
    body = card(0, 0, W, h)
    body += f'<text x="30" y="38" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">{i:02d} · {esc(pr.get("kind","PROJECT").upper())}</text>'
    body += f'<text x="30" y="82" class="serif" font-size="32" font-weight="700" fill="{CREAM}">{esc(pr["name"])}</text>'
    if pr.get("tagline"):
        body += f'<text x="30" y="106" class="serif" font-size="15" font-style="italic" fill="{PINK}">{esc(pr["tagline"])}</text>'
    for j, ln in enumerate(wrap(pr.get("description", ""), 13.5, 520)[:3]):
        body += f'<text x="30" y="{134+j*19}" class="serif" font-size="13.5" fill="{MUTED}">{esc(ln)}</text>'
    tx = 30
    for t in pr.get("tags", [])[:6]:
        tw = int(len(t) * 6.6 + 18)
        body += (f'<rect x="{tx}" y="{h-42}" width="{tw}" height="22" rx="11" fill="none" stroke="{LINE}"/>'
                 f'<text x="{tx+tw/2:.0f}" y="{h-27}" text-anchor="middle" class="mono" font-size="10" fill="{CREAM}">{esc(t)}</text>')
        tx += tw + 8
    sx = 600
    for k, s in enumerate(pr.get("stats", [])[:3]):
        body += (f'<text x="{sx}" y="92" class="serif" font-size="30" font-weight="700" fill="{CREAM}">{esc(s["value"])}</text>'
                 f'<text x="{sx}" y="112" class="mono" font-size="8.5" letter-spacing="1.2" fill="{MUTED}">{esc(s["label"].upper())}</text>')
        sx += max(len(s["value"]) * 18, len(s["label"]) * 8.2, 70) + 22
    if not pr.get("stats"):
        body += f'<text x="{W-40}" y="170" text-anchor="end" class="serif" font-size="110" font-style="italic" font-weight="700" fill="{PINK}" opacity=".16">{i:02d}</text>'
    if pr.get("url") or pr.get("repo"):
        body += f'<text x="{W-30}" y="38" text-anchor="end" class="mono" font-size="10" letter-spacing="1.5" fill="{PINK}">VIEW PROJECT →</text>'
    return svg_doc(W, h, body)


def certs(p):
    groups = p.get("certifications", [])
    cw, gap = 286, 21
    heights = []
    for g in groups:
        n = sum(len(wrap(c, 13, cw - 44)) for c in g["items"])
        heights.append(70 + n * 18 + len(g["items"]) * 6)
    # every card in a row of three gets the height of the tallest one
    row_h = [max(heights[i:i + 3]) for i in range(0, len(heights), 3)]
    body, top = "", 0
    for r, rh in enumerate(row_h):
        for c, g in enumerate(groups[r * 3:r * 3 + 3]):
            x = c * (cw + gap)
            body += card(x, top, cw, rh)
            body += f'<text x="{x+22}" y="{top+32}" class="mono" font-size="9.5" letter-spacing="2" fill="{PINK}">{esc(g["issuer"].upper())}</text>'
            ty = top + 60
            for item in g["items"]:
                for ln in wrap(item, 13, cw - 44):
                    body += f'<text x="{x+22}" y="{ty}" class="serif" font-size="13" fill="{CREAM}">{esc(ln)}</text>'
                    ty += 18
                ty += 6
        top += rh + gap
    return svg_doc(W, max(top - gap, 10), body)


def closing(p):
    first = p["name"].split()[0]
    body = f"""
<rect width="{W}" height="260" rx="20" fill="url(#hero)" stroke="{LINE}"/>
<rect width="{W}" height="260" rx="20" fill="url(#glow)"/>
{brackets(14, 14, W-28, 232, 22)}
<text x="{W/2}" y="150" text-anchor="middle" class="serif" font-size="96" font-style="italic" font-weight="700" fill="{CREAM}" opacity=".92">{esc(first)}</text>
<text x="{W/2}" y="196" text-anchor="middle" class="serif" font-size="16" font-style="italic" fill="{MUTED}">{esc(p.get("closing_line",""))}</text>
<text x="{W/2}" y="232" text-anchor="middle" class="mono" font-size="9.5" letter-spacing="3" fill="{PINK}">{esc(p.get("closing_tags","").upper())}</text>"""
    return svg_doc(W, 260, body)


# ------------------------------------------------------------------ main
def main():
    with open(os.path.join(ROOT, "profile.json"), encoding="utf-8") as f:
        p = json.load(f)
    user = p.get("github_username") or os.environ.get("GITHUB_REPOSITORY_OWNER", "")
    p["github_username"] = user

    photo_b64 = ""
    for ext in ("jpg", "jpeg", "png"):
        fp = os.path.join(ASSETS, f"photo.{ext}")
        if os.path.exists(fp):
            with open(fp, "rb") as f:
                photo_b64 = base64.b64encode(f.read()).decode()
            break

    token = os.environ.get("GITHUB_TOKEN", "")
    try:
        g = fetch_github(user, token) if token and user else sample_github()
    except Exception as e:  # keep building even if the API is unreachable
        print("GitHub API failed, using sample data:", e)
        g = sample_github()

    out = ['<div align="center">', "", f'<img src="assets/hero.svg" width="100%" alt="{esc(p["name"])}">', ""]
    save("hero.svg", hero(p, photo_b64))

    chips = []
    for i, l in enumerate(p.get("links", [])):
        w, s = chip(l["label"], l["text"])
        save(f"chip-{i}.svg", s)
        chips.append(f'<a href="{esc(l["url"])}"><img src="assets/chip-{i}.svg" height="32" alt="{esc(l["label"])}"></a>')
    out += ["<p>" + "&nbsp;&nbsp;".join(chips) + "</p>", "", "</div>", ""]

    def section(fname, num, label, title, img_svg, right="", alt=""):
        save(f"h-{fname}.svg", heading(num, label, title, right))
        save(f"{fname}.svg", img_svg)
        return [f'<img src="assets/h-{fname}.svg" width="100%" alt="{esc(title)}">', "",
                f'<img src="assets/{fname}.svg" width="100%" alt="{esc(alt or title)}">', ""]

    first = p["name"].split()[0]
    n = iter(range(1, 20))
    out += section("about", next(n), "About", f"Hello, I'm {first}.", about(p))
    out += section("skills", next(n), "Stack", "The tools I reach for.", skills(p))
    out += section("commits", next(n), "Commit log", "A year of building.", commit_log(g),
                   right="REAL DATA · REFRESHED DAILY")
    if p.get("achievements"):
        out += section("proof", next(n), "Achievements", "Proof, on the record.", achievements(p))

    out += [f'<img src="assets/h-work.svg" width="100%" alt="Selected work">', ""]
    save("h-work.svg", heading(next(n), "Selected work", "Products, not assignments."))
    for i, pr in enumerate(p.get("projects", []), 1):
        save(f"project-{i}.svg", project(i, pr))
        img = f'<img src="assets/project-{i}.svg" width="100%" alt="{esc(pr["name"])}">'
        link = pr.get("url") or pr.get("repo")
        out += [f'<a href="{esc(link)}">{img}</a>' if link else img, ""]

    total = sum(len(g2["items"]) for g2 in p.get("certifications", []))
    if total:
        out += section("certs", next(n), "Credentials", f"{number_word(total)} credentials, verified.", certs(p))

    save("h-contact.svg", heading(next(n), "Contact", "Let's build something worth explaining."))
    save("closing.svg", closing(p))
    out += ['<img src="assets/h-contact.svg" width="100%" alt="Contact">', "", '<div align="center">',
            f'<img src="assets/closing.svg" width="100%" alt="{esc(first)}">', "", "<p>" + "&nbsp;&nbsp;".join(chips) + "</p>",
            "</div>", ""]

    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Done. Real GitHub data:" , g["real"])


if __name__ == "__main__":
    main()
