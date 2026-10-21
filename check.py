#!/usr/bin/env python3
"""Is my YouTube converter down? Status of popular YouTube to MP3 converter sites.

Each run asks every site's home page once and records whether it answers and where it sends visitors. It does not
try conversions, so a site can answer while its converter is broken.

States
  up          the site answered (403/429 or a bot challenge also counts: the server is there, protecting itself)
  redirected  it now sends visitors to a different domain
  notice      it shows a seizure or shutdown notice
  repurposed  the domain answers but no longer offers a YouTube converter (checked only for sites seen changing)
  down        no answer, a timeout, a DNS failure or a server error (5xx)
A certificate we can't verify is retried without verification and reported as tls="untrusted" instead of down.

Writes (paths relative to this file unless overridden):
  data/latest.json   the current state of every site plus 24-hour uptime
  data/daily.json    per-day counts per site (checks, answered, states, HTTP codes, redirect targets)
  README.md          the table between the status markers

The same checker runs every 10 minutes for the live pages at https://audiofetcher.com/alternatives/
Code: MIT. Data: CC BY 4.0, credit "AudioFetcher (audiofetcher.com)".
"""
from __future__ import annotations

import json
import os
import re
import socket
import ssl
import tempfile
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
OUT = Path(os.environ.get("STATUS_OUT", ROOT / "data" / "latest.json"))
STATE = Path(os.environ.get("STATUS_STATE", ROOT / "data" / "history.json"))
DAILY = Path(os.environ.get("STATUS_DAILY", ROOT / "data" / "daily.json"))
README = Path(os.environ.get("STATUS_README", ROOT / "README.md"))
VANTAGE = os.environ.get("STATUS_VANTAGE", "GitHub Actions")
HISTORY_SEC = 24 * 3600
DAILY_DAYS = 400
TIMEOUT = 12
USER_AGENT = "Mozilla/5.0 (compatible; ConverterStatus/1.0; +https://github.com/yazanbaker94/youtube-converter-status)"
TARGETS = {
    "cnvmp3": ("CnvMP3", "https://cnvmp3.com/", "cnvmp3-not-working"),
    "notube": ("NoTube", "https://notube.net/", "notube-not-working"),
    "savefrom": ("SaveFrom.net", "https://savefrom.net/", "savefrom-not-working"),
    "ytmp3": ("YTMP3", "https://ytmp3.cc/", "ytmp3-not-working"),
    "y2mate": ("Y2Mate", "https://y2mate.com/", "y2mate-shut-down"),
    "yt1s": ("YT1s", "https://yt1s.com/", "yt1s-shut-down"),
    "loader": ("Loader.to", "https://loader.to/", "loader-not-working"),
    "mp3juices": ("MP3Juices", "https://mp3juices.cc/", "mp3juices-not-working"),
    "flvto": ("FLVTO", "https://flvto.biz/", "flvto-not-working"),
    "2conv": ("2conv", "https://2conv.com/", "2conv-not-working"),
    "onlinevideoconverter": ("OnlineVideoConverter", "https://onlinevideoconverter.com/", "onlinevideoconverter-shut-down"),
    "cobalt": ("cobalt", "https://cobalt.tools/", "cobalt-not-working"),
}
# Sites that publish which services they accept. If the site answers but YouTube is missing from that list, it is
# "repurposed" with reason "no-youtube" (cobalt.tools dropped YouTube; its API root lists the supported services).
SERVICE_LISTS = {
    "cobalt": "https://api.cobalt.tools/",
}
CONVERTER_WORDS = re.compile(r"\bmp3\b|youtube (?:to|video|downloader|converter)|video downloader", re.I)
EXPECT_CONVERTER = {"flvto", "2conv"}
NOTICE = re.compile(r"\b(?:ifpi|seized|has been shut ?down|shut down permanently|domain (?:has been|was) seized)\b", re.I)
CHALLENGE = re.compile(r"just a moment|cf-chl|challenge-platform|attention required|ddos-guard", re.I)
LABELS = {"up": "✅ answering", "redirected": "↪️ redirects", "notice": "⛔ shutdown notice",
          "repurposed": "🚫 no longer a converter", "down": "❌ not answering"}


def site(host: str) -> str:
    host = (host or "").lower().split(":")[0]
    return host[4:] if host.startswith("www.") else host


def base_domain(host: str) -> str:
    """en1.savefrom.net and savefrom.net are the same site; only a different main domain is a redirect."""
    return ".".join(site(host).split(".")[-2:])


def fetch(url: str, context: ssl.SSLContext) -> tuple[int, str, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"})
    code, final, body, error = 0, url, "", ""
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
            code, final = response.status, response.geturl()
            body = response.read(65536).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        code, final = exc.code, exc.geturl() or url
        try:
            body = exc.read(65536).decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            body = ""
    except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError, ConnectionError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        error = type(reason).__name__ if not isinstance(reason, str) else reason
    return code, final, body, error


def check(url: str, expect_converter: bool = False) -> dict:
    started = time.monotonic()
    code, final, body, error = fetch(url, ssl.create_default_context())
    tls = ""
    if error == "SSLCertVerificationError":
        unverified = ssl.create_default_context()
        unverified.check_hostname = False
        unverified.verify_mode = ssl.CERT_NONE
        code, final, body, error = fetch(url, unverified)
        tls = "untrusted"
    ms = round((time.monotonic() - started) * 1000)
    final_host = site(urlsplit(final).hostname or "")
    redirected = bool(final_host) and base_domain(final_host) != base_domain(urlsplit(url).hostname or "")
    if error or (code >= 500 and not CHALLENGE.search(body)):
        state = "down"
    elif NOTICE.search(body):
        state = "notice"
    elif redirected:
        state = "redirected"
    elif expect_converter and code < 400 and not CHALLENGE.search(body) and not CONVERTER_WORDS.search(body):
        state = "repurposed"
    else:
        state = "up"
    return {"state": state, "code": code, "ms": ms, "finalHost": final_host if redirected else "", "error": error[:60],
            "tls": tls}


def youtube_supported(url: str) -> bool | None:
    """True/False from a published services list (cobalt's API root: {"cobalt": {"services": [...]}}), None if unknown."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=ssl.create_default_context()) as response:
            data = json.loads(response.read(65536).decode("utf-8", "replace"))
    except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError, ConnectionError, OSError, ValueError):
        return None
    services = (data.get("cobalt") or {}).get("services") if isinstance(data, dict) else None
    if not isinstance(services, list):
        return None
    return any(str(name).lower() == "youtube" for name in services)


def apply_service_lists(results: dict) -> None:
    for key, url in SERVICE_LISTS.items():
        result = results.get(key)
        if not result or result["state"] != "up":
            continue
        supported = youtube_supported(url)
        result["youtube"] = supported
        if supported is False:
            result["state"] = "repurposed"
            result["reason"] = "no-youtube"


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def record_day(daily: dict, now: int, key: str, name: str, result: dict) -> None:
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    days = daily.setdefault("days", {})
    row = days.setdefault(day, {}).setdefault(key, {"name": name, "checks": 0, "answered": 0, "msSum": 0,
                                                     "states": {}, "codes": {}, "finalHosts": {}})
    row["checks"] += 1
    row["answered"] += result["state"] != "down"
    row["msSum"] += result["ms"]
    for field, value in (("states", result["state"]), ("codes", str(result["code"] or result["error"] or "none")),
                         ("finalHosts", result["finalHost"])):
        if value:
            row[field][value] = row[field].get(value, 0) + 1
    cutoff = time.strftime("%Y-%m-%d", time.gmtime(now - DAILY_DAYS * 86400))
    for old in [d for d in days if d < cutoff]:
        del days[old]
    daily["since"] = min(days)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8", newline="\n") as tmp:
        tmp.write(text)
    os.replace(tmp.name, path)


def readme_table(payload: dict) -> str:
    checked = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(payload["checkedAt"]))
    rows = ["| Site | Status right now | Answered (24 h) | Details |", "|---|---|---|---|"]
    for key, t in payload["targets"].items():
        errors = {"gaierror": "domain no longer exists (DNS)", "timeout": "timed out", "TimeoutError": "timed out",
                  "ConnectionRefusedError": "connection refused", "ConnectionResetError": "connection reset"}
        detail = f"→ {t['finalHost']}" if t["finalHost"] else (f"HTTP {t['code']}" if t["code"] else errors.get(t["error"], t["error"]))
        page = f"https://audiofetcher.com/alternatives/{TARGETS[key][2]}/"
        label = "🚫 no YouTube support" if t.get("reason") == "no-youtube" else LABELS.get(t["state"], t["state"])
        rows.append(f"| [{t['name']}]({page}) | {label} | {t['uptime24h']}% | {detail} |")
    return (f"_Last checked {checked} from {VANTAGE}. Each name links to a page explaining what that site's errors "
            f"mean and what happened to it. Live every 10 minutes: "
            f"[audiofetcher.com/alternatives](https://audiofetcher.com/alternatives/)._\n\n" + "\n".join(rows))


def update_readme(payload: dict) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError:
        return
    start, end = "<!-- status:start -->", "<!-- status:end -->"
    if start in text and end in text:
        head, rest = text.split(start, 1)
        _, tail = rest.split(end, 1)
        write(README, f"{head}{start}\n{readme_table(payload)}\n{end}{tail}")


def main() -> None:
    now = int(time.time())
    history = load(STATE, {})
    daily = load(DAILY, {})
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = dict(zip(TARGETS, pool.map(lambda key: check(TARGETS[key][1], key in EXPECT_CONVERTER), TARGETS)))
    apply_service_lists(results)
    targets = {}
    for key, (name, url, _slug) in TARGETS.items():
        result = results[key]
        record_day(daily, now, key, name, result)
        samples = [s for s in history.get(key, []) if now - s["t"] <= HISTORY_SEC]
        samples.append({"t": now, "ok": result["state"] != "down"})
        history[key] = samples
        answered = sum(1 for s in samples if s["ok"])
        targets[key] = {"name": name, "domain": site(urlsplit(url).hostname or ""), **result,
                        "uptime24h": round(answered / len(samples) * 100, 1), "checks24h": len(samples)}
    payload = {"checkedAt": now, "from": VANTAGE, "targets": targets,
               "license": "CC BY 4.0, credit AudioFetcher (https://audiofetcher.com/alternatives/)"}
    write(STATE, json.dumps(history, separators=(",", ":")) + "\n")
    write(DAILY, json.dumps(daily, indent=1, sort_keys=True) + "\n")
    write(OUT, json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    update_readme(payload)
    print(json.dumps({key: (t["state"], t["code"], t["finalHost"]) for key, t in targets.items()}))


if __name__ == "__main__":
    main()
