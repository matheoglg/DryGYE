# DryGYE

DryGYE is a Guayaquil pilot that compares the shortest available route with a route weighted toward lower estimated terrain risk under selectable rain and tide conditions.

## Run locally

1. Create the project environment with `setup_env.bat` on Windows, or install `requirements.txt` in a Python 3.11 environment.
2. From the project root, start the app with:

   ```bash
   python -m app.app
   ```

3. Open `http://127.0.0.1:5000`. Start with **Load demo trip** to use the pre-checked connected route, then toggle the municipal flood reference layer. You can also click two points close to the pilot roads.

The included demo data already contains the risk raster, local municipal road graph, tide table and map reference layers. The fixed demo trip runs without downloading a road graph. Internet is needed for the OpenStreetMap background tiles and fresh Open-Meteo data; the map library itself and pilot routes are local. If tiles are unavailable, the local road, risk and route layers remain visible on a plain map background. Simulation mode works offline. Forecast mode uses a cached forecast if one is available.

## What the prototype shows

- A relative terrain-risk layer derived from elevation above nearby low-elevation pixels, distance to those pixels, and slope.
- A fastest route and a route weighted toward lower estimated terrain risk on the connected part of the pilot road graph. The demo displays snapping distance and warns if no route avoids all very-high-risk edges.
- A toggleable municipal flood-prone reference layer, clearly described as historical/study-based context rather than live flooding or road closures.
- Clearly labeled synthetic rain and tide scenarios. They demonstrate how the routing weight changes; they are not live forecasts or observations.
- An Open-Meteo hourly precipitation point forecast at the city center, shown as a chart and map marker. The forecast has a local cache and can show cached values when the service is unavailable.
- A separate forecast routing mode that uses the center-point 24-hour rain forecast and, when the prepared tide table is available, the current INOCAR tide prediction in the route-risk factor.

## Limits and attribution

The risk surface is a heuristic based on a roughly 30 m digital elevation model. It does not model drainage, street-level water depth, or verified road closures. The route is **lower estimated risk**, not a guaranteed safe route. This prototype is not an official warning service. Municipal road coverage is partial and its source has no one-way attribute, so the pilot graph assumes two-way edges. The flood-reference polygons are not ground truth; the separate spatial sanity check is not a model accuracy score. Official vulnerable-point locations were not available for validation in this prototype. No machine-learning model is claimed, and no model is trained on synthetic scenarios.

The simulation route mode uses synthetic rain and tide. Forecast route mode uses point-forecast rainfall from a model grid near the city center and the INOCAR tide table when available; neither is a street sensor or a flood observation. The local pilot road and flood-reference files were fetched from public Municipio de Guayaquil / MIMG ArcGIS feature services and include source metadata under `data/processed/municipal_reference_metadata.json`. Map tiles come from OpenStreetMap contributors. Terrain input: Copernicus DEM GLO-30. Tide reference included in the project materials: INOCAR. Leaflet 1.9.4 is bundled locally with its BSD license. Retain source attribution and confirm data reuse terms before public distribution.

## Demo verification

- The fixed pilot trip produced 2,843 m fastest (5.7 min) and 3,163 m lower estimated risk (6.3 min) for the heavy-rain/high-tide simulation. Mean estimated risk was 0.702 vs 0.226, with a warning that the alternative still crosses a very-high-risk segment.
- The INOCAR PDF parser produced 355 tide events for October-December 2026; the four 26 October times and heights in the PDF matched the parsed table.
- The municipal layers contain 173 pilot road features and 206 flood-reference polygons. These counts describe the downloaded pilot subset, not citywide coverage.
- A 10-pixel-stride raster comparison found mean heuristic risk 0.461 inside reference polygons (n=157 sampled cells) and 0.252 outside (n=18,899). This is a spatial sanity check against a related reference layer, not independent ground-truth validation or a predictive accuracy score.

The three-person team has two Computing students and one Data Science and AI student. AI tools used: Codex and Claude Code. The team should review and be prepared to explain all code and assumptions. See [the proposal](docs/DryGYE_Proposal.pdf) for scope, sources, safeguards and a next-step plan.
