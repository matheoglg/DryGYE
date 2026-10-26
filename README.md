# DryGYE

DryGYE is a Guayaquil pilot that compares a shortest driving route with a route that has a lower estimated terrain-risk cost under selectable rain and tide scenarios.

## Run locally

1. Create the project environment with `setup_env.bat` on Windows, or install `requirements.txt` in a Python 3.11 environment.
2. From the project root, start the app with:

   ```bash
   python -m app.app
   ```

3. Open `http://127.0.0.1:5000`. Select a scenario, then click an origin and a destination on the map.

The first map load calculates `data/processed/risk.tif` from the included DEM. The first route request downloads and caches a driving graph from OpenStreetMap through OSMnx; internet access is needed unless `data/processed/road_graph.graphml` already exists.

## What the prototype shows

- A relative terrain-risk layer derived from elevation above nearby low-elevation pixels, distance to those pixels, and slope.
- A fastest route and a route weighted toward lower estimated terrain risk.
- Clearly labeled synthetic rain and tide scenarios. They demonstrate how the routing weight changes; they are not live forecasts or observations.
- An Open-Meteo hourly precipitation point forecast at the city center, shown as a chart and map marker. The forecast has a local cache and can show cached values when the service is unavailable.
- A separate forecast routing mode that uses the center-point 24-hour rain forecast in the route-risk factor. Tide is excluded in this mode because a live tide parser is not connected.

## Limits and attribution

The risk surface is a heuristic based on a roughly 30 m digital elevation model. It does not model drainage, street-level water depth, or verified road closures. The route is **lower estimated risk**, not a guaranteed safe route. This prototype is not an official warning service.

The simulation route mode uses synthetic rain and tide. Forecast route mode uses real point-forecast rainfall from a model grid near the city center and excludes tide; it is not a street sensor or a flood observation. No model is trained on synthetic data because it would learn only the simulator's assumptions. Map tiles and driving streets come from OpenStreetMap contributors. Terrain input: Copernicus DEM GLO-30. Tide reference included in the project materials: INOCAR. Verify dataset attribution and applicable terms before public distribution.
