# Is my YouTube converter down? Open status data for YouTube to MP3 sites

Y2Mate, YTMP3, CnvMP3, SaveFrom and the rest come and go: domains move, get seized, or quietly turn into something else. This repository checks **15 popular YouTube to MP3 converter sites** every 3 hours and publishes the results as open data.

## Status right now

<!-- status:start -->
_Last checked 2026-10-24 11:02 UTC from GitHub Actions. Each name links to a page explaining what that site's errors mean and what happened to it. Live every 10 minutes: [audiofetcher.com/alternatives](https://audiofetcher.com/alternatives/)._

| Site | Status right now | Answered (24 h) | Details |
|---|---|---|---|
| [CnvMP3](https://audiofetcher.com/alternatives/cnvmp3-not-working/) | ✅ answering | 100.0% | HTTP 200 |
| [NoTube](https://audiofetcher.com/alternatives/notube-not-working/) | ✅ answering | 100.0% | HTTP 200 |
| [SaveFrom.net](https://audiofetcher.com/alternatives/savefrom-not-working/) | ✅ answering | 100.0% | HTTP 200 |
| [YTMP3](https://audiofetcher.com/alternatives/ytmp3-not-working/) | ↪️ redirects | 100.0% | → yt-to-mp3.net |
| [Y2Mate](https://audiofetcher.com/alternatives/y2mate-shut-down/) | ❌ not answering | 0.0% | domain no longer exists (DNS) |
| [YT1s](https://audiofetcher.com/alternatives/yt1s-shut-down/) | ⛔ shutdown notice | 100.0% | HTTP 200 |
| [Loader.to](https://audiofetcher.com/alternatives/loader-not-working/) | ✅ answering | 100.0% | HTTP 200 |
| [MP3Juices](https://audiofetcher.com/alternatives/mp3juices-not-working/) | ↪️ redirects | 100.0% | → freemp3juice.com |
| [FLVTO](https://audiofetcher.com/alternatives/flvto-not-working/) | 🚫 no longer a converter | 100.0% | HTTP 200 |
| [2conv](https://audiofetcher.com/alternatives/2conv-not-working/) | 🚫 no longer a converter | 100.0% | HTTP 200 |
| [OnlineVideoConverter](https://audiofetcher.com/alternatives/onlinevideoconverter-shut-down/) | ↪️ redirects | 100.0% | → google.com |
| [cobalt](https://audiofetcher.com/alternatives/cobalt-not-working/) | 🚫 no YouTube support | 100.0% | HTTP 200 |
| [EzMP3](https://audiofetcher.com/alternatives/ezmp3-not-working/) | ❌ not answering | 0.0% | domain no longer exists (DNS) |
| [SaveTube](https://audiofetcher.com/alternatives/savetube-not-working/) | ❌ not answering | 0.0% | domain no longer exists (DNS) |
| [X2Download](https://audiofetcher.com/alternatives/x2download-not-working/) | 🚫 no YouTube support | 100.0% | HTTP 200 |
<!-- status:end -->

**What the states mean**
- **answering**: the website responded. It does *not* mean conversions work; this only checks the home page. A `403`, `429` or bot challenge also counts, because the server is up and protecting itself.
- **redirects**: the site now sends visitors to a different domain, shown under Details.
- **shutdown notice**: the page shows a seizure or shutdown notice.
- **no longer a converter**: the domain answers but no longer offers a YouTube converter.
- **no YouTube support**: the site still works for other platforms but no longer accepts YouTube links.
- **not answering**: timeout, DNS failure or server error.

## Data

| File | What it is |
|---|---|
| [`data/latest.json`](data/latest.json) | The latest check of every site, with 24-hour uptime |
| [`data/daily.json`](data/daily.json) | Per-day counts per site: checks, answers, states, HTTP codes and redirect targets |

A faster live feed (every 10 minutes, from a server in Canada) is at `https://audiofetcher.com/status/converters.json`, and the explanation pages are at **[audiofetcher.com/alternatives](https://audiofetcher.com/alternatives/)**.

From November 2026, a monthly report at audiofetcher.com/reports/ sums up which converters worked, moved or disappeared that month.

## Run it yourself

```bash
python check.py
```

Python 3.9+ with no dependencies. It writes `data/latest.json`, `data/daily.json` and the table above. To change which sites are checked, edit `TARGETS` in `check.py`.

## Method and limits

- One `GET` of each home page per run, with an honest User-Agent that links to this repository, from GitHub's servers.
- A site can answer while its converter fails (YouTube blocks, broken backends), so "answering" is an upper bound.
- Results depend on where the check runs from: a site blocked in one country may work in another.
- Facts about what happened to each site (IFPI's closure of Y2Mate in October 2025, court-ordered blocks and so on) are sourced on the linked pages.

## License

- Code: [MIT](LICENSE)
- Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Please credit "AudioFetcher (audiofetcher.com)" with a link.

Maintained by [AudioFetcher](https://audiofetcher.com/), an ad-free YouTube to MP3 converter. Disclosure: AudioFetcher is itself a converter, so it isn't in this list; the checks are the same for every site above.
