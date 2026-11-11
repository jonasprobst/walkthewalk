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
6. **fun extras** (all opt-in, default off): rooftop detector, secret powers, sounds (WebAudio), coins. Building outlines come from the Overpass API once per trip and are cached on the trip as `tr.roofs`.
7. **3D mode** (opt-in, only offered for trips starting in Switzerland): CesiumJS 1.124 loaded on demand, with swisstopo terrain, SWISSIMAGE aerial tiles and swissBUILDINGS3D 3D Tiles. State in global `D3`. `d3Render` moves the buddy billboard, clamps it to roof/ground height and drives the camera (chase / bird / free).

## Conventions

- Bump the version string in the footer (`<span id="ver">Version N · date</span>`) with every pushed change; the owner uses it to check what the phone has.
- New fun features are opt-in and remembered in `prefs`.
- Kid-facing text: short, friendly, with emoji. No `alert/confirm`; use the built-in modals and `toast()` / `homeToast()`.
- The repo is public. Do not commit the owner's real GPS tracks or personal details.
- Credit lines must stay: OpenStreetMap contributors, swisstopo.

## What has and hasn't been verified

Verified in headless Chrome with the Leaflet stand-in: import, storage, replay, stats, extras logic (with fake building data), finish screen, phone and desktop layouts, version footer and reload.

**Never seen running by the previous agent** (its sandbox could not reach these hosts):

- Real Leaflet with OSM tiles. One real bug was found this way by the owner and fixed (marker element requested before the map had a view).
- Overpass rooftop lookup against real data.
- The whole Cesium 3D mode: only the control flow was exercised with a Proxy stand-in. Service URLs were taken from docs.geo.admin.ch. Likely trouble spots: Viewer options, imagery URL/levels, `clampToHeight` behaviour on the phone, camera heading, ground-clamped polylines over 3D tiles, performance.

So: get real network access (or have the owner test) before trusting any of that.

## Open items

1. **Bugs.** The owner reports "a couple of minor bugs" but has not described them yet. Ask for them (screenshots help) before changing anything.
2. **Bern button / offline test map.** The owner asked to "add Bern as a button and make the 3D version of Bern the offline test map". It was not clarified. Open questions: should the button open free 3D exploration of Bern, a demo walk, or both? Does "offline" mean caching on the phone (service worker), a full pre-download, or Bern data checked into the repo? Note the privacy point above if a demo walk is wanted.
3. In 3D mode, coins, sparkles and gold roof highlights are not drawn (counter, toasts and sounds work).
4. `localStorage` is small (about 5 MB). Many long trips will hit the limit; IndexedDB would fix that.
5. The app needs internet for map tiles; there is no service worker yet.
6. GitHub Pages was enabled by hand in the repo settings (deploy from branch `main`, `/`).
