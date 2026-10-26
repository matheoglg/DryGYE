# DryGYE

DryGYE is a Guayaquil pilot that compares the shortest available route with a route weighted toward lower estimated terrain risk under selectable rain and tide conditions.

## Run locally

1. Create the environment: `setup_env.bat -Mode venv` on Windows (creates `.venv` with Python 3.10–3.12 and installs `requirements.txt`), or `setup_env.bat` for conda.
2. From the project root, start the app with either command:

   ```bash
   .venv\Scripts\python.exe app\app.py
   .venv\Scripts\python.exe -m app.app
   ```

3. Open `http://127.0.0.1:5000`. Press **Demo trip**, or click a start and an end point on the map and press **Calculate routes**. Click any route line or route card to view it.

The included demo data already contains the risk raster, the pilot street graph, the tide table and the flood reference layer, so routing works offline. To rebuild the street graph (needs internet): `python scripts/build_road_graph.py`. It downloads drivable streets from the main OpenStreetMap API in small tiles, because Overpass is often unreachable. Internet is needed for the OpenStreetMap background tiles and fresh Open-Meteo data; the map library itself and pilot routes are local. If tiles are unavailable, the local road, risk and route layers remain visible on a plain map background. Simulation mode works offline. Forecast mode uses a cached forecast if one is available.

## What the prototype shows

- A relative terrain-risk layer derived from elevation above nearby low-elevation pixels, distance to those pixels, and slope.
- A fastest route, a route weighted toward lower estimated terrain risk and up to two alternative routes, on the OpenStreetMap street network of the pilot area (largest strongly connected part, respecting one-way streets). Route lines follow the street shapes from the chosen start point to the chosen end point. The app warns if no route avoids all very-high-risk streets.
- A toggleable municipal flood-prone reference layer, clearly described as historical/study-based context rather than live flooding or road closures.
- Clearly labeled synthetic rain and tide scenarios. They demonstrate how the routing weight changes; they are not live forecasts or observations.
- An Open-Meteo hourly precipitation point forecast at the city center, shown as a chart. The forecast has a local cache and can show cached values when the service is unavailable.
- A separate forecast routing mode that uses the center-point 24-hour rain forecast and, when the prepared tide table is available, the current INOCAR tide prediction in the route-risk factor.

## Limits and attribution

The risk surface is a heuristic based on a roughly 30 m digital elevation model. It does not model drainage, street-level water depth, or verified road closures. The route is **lower estimated risk**, not a guaranteed safe route. This prototype is not an official warning service. OpenStreetMap street data is community-mapped and may miss streets or turn restrictions. The flood-reference polygons are not ground truth; the separate spatial sanity check is not a model accuracy score. Official vulnerable-point locations were not available for validation in this prototype. No machine-learning model is claimed, and no model is trained on synthetic scenarios.

The simulation route mode uses synthetic rain and tide. Forecast route mode uses point-forecast rainfall from a model grid near the city center and the INOCAR tide table when available; neither is a street sensor or a flood observation. The flood-reference file was fetched from public Municipio de Guayaquil / MIMG ArcGIS feature services and include source metadata under `data/processed/municipal_reference_metadata.json`. Map tiles and the street network come from OpenStreetMap contributors (ODbL). Terrain input: Copernicus DEM GLO-30. Tide reference included in the project materials: INOCAR. Leaflet 1.9.4 is bundled locally with its BSD license. Retain source attribution and confirm data reuse terms before public distribution.

## Demo verification

- The demo trip (Urdesa / Kennedy area, flooded on 24 October 2026) produced 4,092 m fastest (8.2 min) and 4,373 m lower estimated risk (8.7 min) in the heavy-rain/high-tide simulation. Mean estimated risk was 0.322 vs 0.132. Two alternatives: 4,570 m (0.251) and 5,176 m (0.168).
- The covered area runs from Guasmo / Isla Trinitaria (south) to Samanes / Sauces (north) and west to Monte Sinai (`PILOT_BBOX` in `drygye/config.py`); it is drawn on the map as a dashed border. Its street graph has 36,139 nodes and 99,597 directed edges and loads in about 9 s at startup.
- The INOCAR PDF parser produced 355 tide events for October-December 2026; the four 26 October times and heights in the PDF matched the parsed table.
- The municipal flood-reference layer contains 1,136 polygons (simplified to about 5 m). These counts describe the downloaded pilot subset, not citywide coverage.
- A 10-pixel-stride raster comparison found mean heuristic risk 0.461 inside reference polygons (n=157 sampled cells) and 0.252 outside (n=18,899). This is a spatial sanity check against a related reference layer, not independent ground-truth validation or a predictive accuracy score.

The three-person team has two Computing students and one Data Science and AI student. AI tools used: Codex and Claude Code. The team should review and be prepared to explain all code and assumptions. See [the proposal](docs/DryGYE_Proposal.pdf) for scope, sources, safeguards and a next-step plan.
