"""Smoke test: runs index.html in headless Chrome with a stand-in for Leaflet (test/mockL.js),
so it works without network. Checks import, replay, extras toggles and the finish screen.
Usage: python3 test/smoke.py      (needs: pip install playwright; set CHROME=/path/to/chrome to use a system browser)
The real map tiles, Overpass and the Cesium 3D mode are NOT covered: check those in a real browser."""
import json, os, pathlib, tempfile
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parent.parent
tmp = pathlib.Path(tempfile.mkdtemp())
html = (root / 'index.html').read_text(encoding='utf-8')
tag = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
assert tag in html
(tmp / 't.html').write_text(html.replace(tag, '<script src="mockL.js"></script>'), encoding='utf-8')
(tmp / 'mockL.js').write_text((root / 'test' / 'mockL.js').read_text())

# synthetic Columbus-format track in Bern: 20 min, one point per second
lines = ['# Format=ColumbusFusion; Version=1.0; Type=GNSS', 'tag,date,time,lat,lon,alt,speed,heading']
for i in range(1200):
    t = 100000 + (i // 3600) * 10000 + (i % 3600 // 60) * 100 + i % 60
    lines.append(f"{'T' if i == 0 else ''},{'261031' if i == 0 else ''},{t:06d},{46.948 + i * 0.00001:.7f},{7.447 + i * 0.000012:.7f},{540 + i % 7},{4.0 + i % 3},90.0")
(tmp / 'trip.CSV').write_text('\n'.join(lines))

with sync_playwright() as p:
    kw = {'args': ['--no-sandbox']}
    if os.environ.get('CHROME'): kw['executable_path'] = os.environ['CHROME']
    b = p.chromium.launch(**kw)
    pg = b.new_page(viewport={'width': 390, 'height': 844})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # stand-in for Overpass: the first answer is an overloaded server ("200 OK", empty list, remark), which must not be
    # taken for "no houses"; after that, one house that the path crosses around points 100-110
    asked = []
    house = [[46.94899, 7.44815], [46.94911, 7.44815], [46.94911, 7.44835], [46.94899, 7.44835], [46.94899, 7.44815]]
    def overpass(r):
        asked.append(r.request.url)
        if len(asked) == 1: body = {'elements': [], 'remark': 'runtime error: Query timed out in "query" at line 1 after 26 seconds.'}
        else: body = {'elements': [{'type': 'way', 'id': 1, 'geometry': [{'lat': a, 'lon': o} for a, o in house]}]}
        r.fulfill(status=200, content_type='application/json', body=json.dumps(body))
    pg.route('**/api/interpreter', overpass)
    pg.goto((tmp / 't.html').as_uri()); pg.wait_for_timeout(300)
    assert pg.locator('.card:not(.add)').count() == 0
    pg.set_input_files('#fileIn', str(tmp / 'trip.CSV')); pg.wait_for_timeout(400)
    assert pg.locator('.card:not(.add)').count() == 1, 'import failed'
    pg.click('.card:not(.add)'); pg.wait_for_timeout(200)
    pg.click('#funFromPicker')
    for k in range(4): pg.click(f'.funRow >> nth={k}')
    pg.click('#funDone'); pg.click('#buddies button >> nth=0'); pg.wait_for_timeout(800)
    assert pg.evaluate('S.playing'), 'not playing'
    assert pg.is_visible('#d3Btn'), '3D button should show for Swiss trips'
    pg.wait_for_function('cur.roofs && !roofJob', timeout=5000)
    assert len(asked) >= 2 and asked[0] != asked[1], 'an overloaded answer should send the question to the next server'
    assert pg.evaluate('cur.roofs.bld.length') == 1, 'house on the path not found'
    assert pg.evaluate('JSON.parse(localStorage.getItem(STORE))[0].roofs.bld.length') == 1, 'rooftops not saved with the trip'
    # the same walk logged every 5 s (single points on the house) must find the same roof
    assert pg.evaluate('analyseRoofs({pts: cur.pts.filter((p, i) => i % 5 === 3)}, [HOUSE]).bld.length'.replace('HOUSE', json.dumps(house))) == 1, 'slow logger misses the roof'
    pg.evaluate('seek(P.vEnd - 2); S.playing = true'); pg.wait_for_timeout(1500)
    assert pg.is_visible('#endModal.on'), 'finish screen missing'
    assert not errs, errs
    print('OK', pg.inner_text('#ver'))
    b.close()
