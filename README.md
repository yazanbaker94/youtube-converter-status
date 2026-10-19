# Is my YouTube converter down? Open status data for YouTube to MP3 sites

Y2Mate, YTMP3, CnvMP3, SaveFrom and the rest come and go: domains move, get seized, or quietly turn into something else. This repository checks **11 popular YouTube to MP3 converter sites** every 3 hours and publishes the results as open data.

## Status right now

<!-- status:start -->
_The first automatic check will fill this table in._
<!-- status:end -->

**What the states mean**
- **answering**: the website responded. It does *not* mean conversions work; this only checks the home page. A `403`, `429` or bot challenge also counts, because the server is up and protecting itself.
- **redirects**: the site now sends visitors to a different domain, shown under Details.
- **shutdown notice**: the page shows a seizure or shutdown notice.
- **no longer a converter**: the domain answers but no longer offers a YouTube converter.
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
