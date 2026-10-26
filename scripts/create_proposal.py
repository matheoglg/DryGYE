"""Create the English Hack2Impact proposal PDF for DryGYE."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "DryGYE_Proposal.pdf"
NAVY = colors.HexColor("#123047")
TEAL = colors.HexColor("#087f76")
PALE = colors.HexColor("#e9f5f3")
INK = colors.HexColor("#243746")
MUTED = colors.HexColor("#526575")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
                          fontSize=26, leading=29, textColor=NAVY, alignment=TA_LEFT, spaceAfter=6))
styles.add(ParagraphStyle(name="Deck", parent=styles["Normal"], fontSize=13, leading=19,
                          textColor=MUTED, spaceAfter=14))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold",
                          fontSize=12.5, leading=15, textColor=NAVY, spaceBefore=7, spaceAfter=3.5,
                          keepWithNext=True))
styles.add(ParagraphStyle(name="Body2", parent=styles["BodyText"], fontSize=8.7, leading=11.3,
                          textColor=INK, spaceAfter=3.5))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=7.5, leading=10,
                          textColor=MUTED, spaceAfter=3))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontSize=11, leading=15,
                          textColor=NAVY, spaceAfter=2))
styles.add(ParagraphStyle(name="Kicker", parent=styles["Normal"], fontSize=9, leading=12,
                          textColor=TEAL, fontName="Helvetica-Bold", spaceAfter=12))


def P(text, style="Body2"):
    return Paragraph(text, styles[style])


def footer(canvas, doc):
    canvas.saveState()
    w, _ = letter
    canvas.setStrokeColor(colors.HexColor("#d9e3e9"))
    canvas.line(0.65*inch, 0.52*inch, w-0.65*inch, 0.52*inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.68*inch, 0.34*inch, "DRYGYE  |  HACK2IMPACT 2026  |  GUAYAQUIL PILOT")
    canvas.drawRightString(w-0.68*inch, 0.34*inch, f"{doc.page}")
    canvas.restoreState()


def bullets(items):
    return [P("- " + item) for item in items]


def section(title, text):
    return [P(title, "Section"), P(text)]


OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=.68*inch,
                        leftMargin=.68*inch, topMargin=.5*inch, bottomMargin=.62*inch,
                        title="DryGYE - Rain-aware route comparison for Guayaquil",
                        author="DryGYE team | Hack2Impact 2026")
story = []

# Page 1: Problem and proposed product
story += [Spacer(1, .18*inch), P("HACK2IMPACT 2026  /  NU ZETA  /  ESPOL", "Kicker"),
          P("DryGYE", "CoverTitle"),
          P("A rain-aware map for comparing routes in Guayaquil", "Deck")]
callout = Table([[P("ANTICIPATE  &nbsp; / &nbsp;  COMPARE  &nbsp; / &nbsp;  EXPLAIN", "Kicker")],
                 [P("When intense rain is expected, DryGYE helps a resident or local responder compare a short route with one that has lower <b>estimated terrain risk</b> inside a clearly bounded pilot area.", "Callout")]], colWidths=[7.12*inch])
callout.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PALE),("BOX",(0,0),(-1,-1),.7,colors.HexColor("#c5e6df")),
                             ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),
                             ("TOPPADDING",(0,0),(-1,0),9),("BOTTOMPADDING",(0,0),(-1,0),1),
                             ("TOPPADDING",(0,1),(-1,1),1),("BOTTOMPADDING",(0,1),(-1,1),11)]))
story += [callout, Spacer(1, 8)]
story += section("The problem", "Intense rain can disrupt movement across Guayaquil, while rainfall, high tide and vulnerable terrain can overlap. A citywide forecast does not tell a person which of two nearby streets has the lower relative exposure. DryGYE addresses this narrow decision-support gap in a pilot map; it does not issue official warnings or confirm that roads are passable.")
story += section("The solution", "A browser-based map brings together a terrain-risk estimate, a point rainfall forecast, predicted tides, and a cached pilot road network. The user can choose simulation or forecast conditions, inspect a municipal flood-reference layer, and compare the shortest available route with a route weighted toward lower estimated risk. A fixed demo trip makes the core workflow repeatable.")
story += [P("What the prototype demonstrates", "Section")]
tbl = [[P("INPUT", "Small"), P("MAP", "Small"), P("DECISION SUPPORT", "Small")],
       [P("Rain scenario or Open-Meteo point forecast; INOCAR tide prediction when the local table covers the current time.", "Body2"),
        P("Relative terrain heuristic, municipal road segments, and a separate historical/study-based flood reference layer.", "Body2"),
        P("Fastest route vs. lower estimated-risk route, with distance, estimated time, risk summary and a high-risk-edge warning.", "Body2")]]
t=Table(tbl,colWidths=[2.34*inch]*3)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                       ("VALIGN",(0,0),(-1,-1),"TOP"),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d5e0e5")),
                       ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                       ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
story += [t, Spacer(1,5), P("Pilot focus: a bounded urban area in Guayaquil with 173 municipal road features and a prebuilt local graph. Coverage is partial; the demo trip is anchored to the connected portion of that graph.", "Small"), PageBreak()]

# Page 2: implementation, evidence, limits
story += [P("HOW IT WORKS", "Kicker"), P("A transparent prototype", "CoverTitle"),
          P("The system favors inspectable data and explicit assumptions over unsupported claims of predictive accuracy.", "Deck")]
story += [P("Technical approach", "Section")]
story += bullets([
    "<b>Terrain layer:</b> a 0-1 relative heuristic from Copernicus DEM GLO-30 elevation context, distance to low-elevation pixels and slope. It is not a street-water-depth model.",
    "<b>Road network:</b> a local NetworkX graph built from the municipality's public road layer, saved as GraphML so route calculation does not need a live network download. The source has no one-way field, so pilot edges are treated as bidirectional.",
    "<b>Dynamic conditions:</b> selectable synthetic scenarios are visibly labeled simulation. Forecast mode uses Open-Meteo hourly precipitation at a city-center grid point and interpolated INOCAR tide predictions from the provided PDF when the table covers the current time.",
    "<b>Route comparison:</b> NetworkX shortest path by length and by an explicitly weighted terrain-risk cost. Very-high-risk edges are avoided on red alerts when a feasible path exists; the interface warns when it cannot avoid every such segment.",
    "<b>Map references:</b> 206 municipal flood-prone reference polygons can be toggled separately. They describe historical/study-based zones, not live water or current closures."
])
story += [P("Checks completed for the demo", "Section")]
rows = [[P("CHECK", "Small"), P("OBSERVED RESULT", "Small")],
        [P("INOCAR PDF parse", "Body2"), P("355 tide events parsed for Oct-Dec 2026. The four listed events on 26 Oct match the PDF: 01:45 0.80 m; 06:51 4.50 m; 14:15 0.55 m; 19:31 4.50 m.", "Body2")],
        [P("Fixed pilot route", "Body2"), P("Under the heavy-rain/high-tide simulation: fastest 2,843 m / 5.7 min; lower-cost route 3,163 m / 6.3 min; mean estimated risk 0.702 vs 0.226. Both endpoints snap to the graph at 0 m. The response flags a remaining very-high-risk segment.", "Body2")],
        [P("Flood-reference sanity check", "Body2"), P("At a 10-pixel sampling stride: mean heuristic risk 0.461 inside reference polygons (n=157) and 0.252 outside (n=18,899). This is a spatial sanity check against a related reference layer, not independent ground truth or a model-accuracy score.", "Body2")]]
t=Table(rows,colWidths=[1.45*inch,5.57*inch],repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                       ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d5e0e5")),("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
                       ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
                       ("BACKGROUND",(0,1),(-1,-1),colors.white)]))
story += [t, P("Known limits and safeguards", "Section")]
story += bullets([
    "Relative heuristic risk is not a flood forecast, sensor reading, official warning or guarantee of safe travel.",
    "Road coverage is a small pilot and connectivity is incomplete. Missing roads, access restrictions and real-time closures are not represented; modeled edges assume two-way travel.",
    "Rain is a single forecast grid point, not street-level rainfall. Tide predictions are astronomical predictions, not observations of local inundation.",
    "The public flood polygons are context, not ground truth. The 74 vulnerable point locations were not available for this prototype's validation.",
    "No machine-learning model is claimed. Synthetic data support scenario demonstrations only; training on it would reproduce simulator assumptions rather than establish real-world accuracy."
])
story += [PageBreak()]

# Page 3: impact, plan, team and sources
story += [P("DELIVERY & NEXT STEPS", "Kicker"), P("From demo to a responsible pilot", "CoverTitle"),
          P("The prototype is a decision-support concept for residents and local response teams, with a practical path from a local demo to a responsibly validated pilot.", "Deck")]
story += [P("Expected value", "Section"), P("For the bounded pilot, DryGYE makes the interaction between forecast rain, predicted tide and relative terrain exposure visible in one place. Route alternatives are presented with their trade-offs instead of a single opaque recommendation. The immediate outcome is a reproducible demonstration and a concrete validation plan, not a claim of lives saved or operational deployment.")]
story += [P("Implementation roadmap", "Section")]
plan = [[P("PHASE", "Small"),P("WORK", "Small"),P("EXIT CRITERION", "Small")],
        [P("1. Data readiness", "Body2"),P("Obtain permissioned road, flood reference and official vulnerable-point data; document coverage, coordinate systems, dates and reuse terms.", "Body2"),P("Versioned data inventory and reproducible preprocessing.", "Body2")],
        [P("2. Field validation", "Body2"),P("Work with municipal / community partners to compare route estimates with observed water reports and road closures across multiple rain events.", "Body2"),P("Independent validation protocol, uncertainty measures and known failure cases.", "Body2")],
        [P("3. Improve routing", "Body2"),P("Add verified one-way/access restrictions, network coverage checks, and time-sensitive closure inputs; retain fallback to cached graph.", "Body2"),P("Routes checked against a trusted routing baseline and reviewed by local stakeholders.", "Body2")],
        [P("4. Responsible pilot", "Body2"),P("Co-design user messages, accessibility and alert escalation with local agencies; monitor data freshness and update cadence.", "Body2"),P("Limited pilot only after safety, privacy and operational review.", "Body2")]]
t=Table(plan,colWidths=[1.18*inch,3.52*inch,2.32*inch],repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                       ("GRID",(0,0),(-1,-1),.4,colors.HexColor("#d5e0e5")),("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
                       ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
story += [t, P("Team and tools", "Section"), P("Three ESPOL students: two in Computing and one in Data Science and AI. The prototype uses Python, Flask, Leaflet, NetworkX, OSMnx-compatible GraphML, rasterio, NumPy, Shapely and public ArcGIS feature services. Data sources: Municipio de Guayaquil / MIMG road and flood-reference layers; Copernicus DEM GLO-30; Open-Meteo point forecast; INOCAR tide table. AI tools used: Codex and Claude Code. The team reviewed and should be prepared to explain all submitted code and assumptions.")]
story += [P("Sources", "Section"),
          P('Municipal road feature service: <link href="https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Estructura_vial_%C3%A1rea_urbana/FeatureServer" color="#087f76">Guayaquil urban road structure</link>. Municipal flood-reference service: <link href="https://services7.arcgis.com/NWWHhu45fOJtCgG3/arcgis/rest/services/Zonas_Inundables_GYE/FeatureServer" color="#087f76">Flood-prone zones reference</link>. The layer metadata describes these zones as study- and historical-event-based; they are not live closures.', "Small"),
          P('ATM vulnerable-point context: <link href="https://atm.gob.ec/puntos-vulnerables-guayaquil/" color="#087f76">Puntos vulnerables de Guayaquil</link>. INOCAR tide reference: <link href="https://www.inocar.mil.ec/" color="#087f76">Instituto Oceanografico y Antartico de la Armada</link>. Open-Meteo: <link href="https://open-meteo.com/" color="#087f76">Forecast API</link>. Copernicus DEM: <link href="https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model" color="#087f76">GLO-30 collection</link>.', "Small"),
          Spacer(1,5), P("DryGYE is a student prototype. It is not an official emergency or navigation service.", "Small")]

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
