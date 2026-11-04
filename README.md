# Flight Display

A small local dashboard that shows the nearest airborne aircraft to a configured
search area. A Python polling script reads public ADS-B data and writes a compact
`flight.json` file that the static dashboard displays.

**Built with:** Python standard library, HTML, CSS, and JavaScript.

## What it demonstrates

- Polling and normalizing public JSON APIs.
- Defensive handling of temporary network and route-lookup failures.
- A simple static UI that refreshes from generated JSON without inserting remote
  data as HTML.

## Run locally

1. Copy `.env.example` to `.env` and choose an approximate search area. The values
   are coordinates, not secrets; keep a precise personal location out of a public repo.
2. In one terminal, run:

   ```sh
   set -a; source .env; set +a
   python3 main.py
   ```

3. In another terminal, serve the folder:

   ```sh
   python3 -m http.server 8000
   ```

4. Open `http://localhost:8000`.

`main.py` refreshes the generated `flight.json` about every 30 seconds. Stop it
with Control-C. This project is designed as a local demo; static hosting alone
will not run the polling process.

## Data sources

The project queries public endpoints from [ADSB.lol](https://api.adsb.lol/) and
[ADSBDB](https://api.adsbdb.com/). Availability and accuracy depend on those
services. Check their terms and rate limits before deploying or increasing the
polling frequency.

## Repository note

`flight.json` is generated locally and intentionally ignored. This source is
shared for portfolio and review purposes; please ask before reusing it.
