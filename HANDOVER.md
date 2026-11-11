# Handover: Walk the Walk (Adventure Replay)

Written 11 Nov 2026 for whoever picks this up next (Claude Code).

## What this is

A single-page web app for a child aged 6–9 to replay family GPS tracks on a map. The owner's son picks a trip, picks a buddy character, and watches it walk the route. Live at https://jonasprobst.github.io/walkthewalk/ (GitHub Pages, `main` branch, root folder). Mainly used in Chrome on an Android phone; must also work on desktop.

## Files

- `index.html`: the whole app (HTML, CSS, JS in one file, no build step). Edit it directly.
- `test/smoke.py`, `test/mockL.js`: headless smoke test with a stand-in for Leaflet. Run `python3 test/smoke.py`.
- `README.md`: public description with the app link.

## How the app is organised (sections in `index.html`, in order)

1. **helpers / parsing**: `parseCSV` reads Columbus logger files (`tag,date,time,lat,lon,alt,speed,heading`; date only on the first row; times are UTC `HHMMSS`; speed in km/h). `parseGPX` reads GPX. `parseTrack` returns `{start, pts:[[tSec, lat, lon, alt, speed, poi], …]}`.
2. **prepare(tr)**: builds typed arrays in the global `P` (times, positions, smoothed speed/altitude, cumulative distance, climb). Gaps over 8 s are compressed into "virtual time" `VT` so the replay doesn't freeze.
3. **storage**: trips live in `localStorage` key `adventureReplay.tracks.v1`; settings in `adventureReplay.prefs.v1` (`buddy`, `fun{roofs,powers,sounds,coins}`, `d3`). Nothing is uploaded.
4. **home screen**: cards with SVG route thumbnails, add/rename/delete, version footer and "Get newest version" button.
5. **player (flat map)**: Leaflet + OpenStreetMap raster tiles. State in global `S`. `openTrackInner` sets up a trip, `render()` runs per frame, `seek()` jumps. The buddy is a `divIcon` pin whose tip is the exact position.
6. **fun extras** (all opt-in, default off): rooftop detector, secret powers, sounds (WebAudio), coins. Building outlines come from the Overpass API once per trip and are cached on the trip as `tr.roofs` (`v: 2`; older answers are looked up again). The path is asked in pieces of 80 points (`roofQueries`), each piece tries the servers in turn with a 20 s limit (`askOverpass`), and a failed lookup is retried by itself and never saved (`roofRun`). `analyseRoofs` checks the path between GPS points every ~2 m.
7. **3D mode** (opt-in, only offered for trips starting in Switzerland): CesiumJS 1.124 loaded on demand, with swisstopo terrain, SWISSIMAGE aerial tiles and swissBUILDINGS3D 3D Tiles. State in global `D3`. `d3Render` moves the buddy billboard, clamps it to roof/ground height and drives the camera (chase / bird / free).

## Conventions

- Bump the version string in the footer (`<span id="ver">Version N · date</span>`) with every pushed change; the owner uses it to check what the phone has.
- New fun features are opt-in and remembered in `prefs`.
- Kid-facing text: short, friendly, with emoji. No `alert/confirm`; use the built-in modals and `toast()` / `homeToast()`.
- The repo is public. Do not commit the owner's real GPS tracks or personal details.
- Credit lines must stay: OpenStreetMap contributors, swisstopo.

## What has and hasn't been verified

Verified by `test/smoke.py` (headless Chrome, Leaflet stand-in, no network): import, storage, replay, stats, extras logic, an overloaded Overpass answer not being cached, slow-logger roof detection, finish screen, version footer.

Verified on 11 Nov 2026 in headless Chromium against the real services, with a made-up straight-line walk through Bern:

- Real Leaflet with OSM tiles.
- Rooftop lookup with real building data from `overpass.osm.ch`.
- 3D mode: Cesium loads, swisstopo terrain, SWISSIMAGE and swissBUILDINGS3D draw, the buddy stands on roof/ground height, chase and bird camera, gold roofs.

Not verified:

- `overpass-api.de`, `overpass.kumi.systems` and `overpass.private.coffee` refused or hung from the test sandbox, so the app was only seen working through the Swiss server. Whether they behave on the owner's phone is unknown.
- Anything on a real Android phone: 3D speed, touch, `clampToHeight` on a phone GPU.
- The owner's real tracks (logging interval, GPS drift). Not in the repo on purpose.

Testing tips: Cesium's workers do not run from `file://`, so serve the folder (`python3 -m http.server`) to test 3D. Headless Chromium needs `--use-angle=swiftshader --enable-unsafe-swiftshader` for WebGL. `CHROME=/path/to/chrome python3 test/smoke.py` uses a system browser.

## Open items

1. **Bugs.** The owner reports "a couple of minor bugs" but has not described them yet. Ask for them (screenshots help) before changing anything.
   - **Rooftop detection worked sometimes and sometimes not: fixed in version 8**, waiting for the owner to confirm on the phone. Causes found, each reproduced first:
     - Long trips never worked: one `around:` query with ~1200 points takes minutes (100 points 2.4 s, 200 points 12 s, 1200 points timeout / HTTP 500 on a real server). Now asked in pieces of 80 points.
     - An overloaded server answers HTTP 200 with an empty list and a `remark`; this was saved as "no houses" for good. Now treated as a failure. A rate-limited server answers HTTP 200 with an HTML page (`duplicate_query`, `rate_limited`).
     - No time limit on requests: a hanging server meant "Looking for rooftops…" for ever. Now 20 s, then the next server.
     - A failure was not retried until the trip was reopened. Now retried after 5, 10, 20, 40, 60 s, and at once when the phone comes back online.
     - Only GPS points were tested, and 2 in a row were needed, so a logger writing every 5 s found half the roofs (14 instead of 29 on the test walk). Now the path between points is tested too (25 of 29).
     - 3D mode drew no gold roofs. Now it does (`d3SyncLit`).
     - Still open: rooftops depend on GPS drift, because nobody walks through houses. A walk beside a house is a roof only if the track wobbles 4+ m into the outline. If `localStorage` is full, `tr.roofs` isn't saved and is fetched again each time.
2. **Bern button / offline test map.** The owner asked to "add Bern as a button and make the 3D version of Bern the offline test map". It was not clarified. Open questions: should the button open free 3D exploration of Bern, a demo walk, or both? Does "offline" mean caching on the phone (service worker), a full pre-download, or Bern data checked into the repo? Note the privacy point above if a demo walk is wanted.
3. In 3D mode, coins and sparkles are not drawn (counter, toasts and sounds work). Gold roofs are drawn since version 8.
4. `localStorage` is small (about 5 MB). Many long trips will hit the limit; IndexedDB would fix that.
5. The app needs internet for map tiles; there is no service worker yet.
6. GitHub Pages was enabled by hand in the repo settings (deploy from branch `main`, `/`).
