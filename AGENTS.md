# DryGYE — contexto del proyecto (Hack2Impact 2026, reto Guayaquil)

Este archivo (`AGENTS.md`) es el contexto compartido para cualquier asistente de IA o persona del equipo (Codex, Copilot, Cursor, Gemini, ChatGPT, etc.). Si tu herramienta no lo lee sola, pégalo al inicio de la conversación. Lee este archivo completo antes de tocar nada. Es el contexto que el equipo (3 estudiantes de ESPOL) armó investigando antes del evento.

## 0. Reglas para el asistente de IA

- **Antes de las 15h00 del lunes 26-oct-2026 (hora Ecuador):** no escribas código del proyecto. Desde las 15h00 ya se puede desarrollar y hacer commits (regla 6.6).
- **Commits:** usa la identidad git local de cada persona. Si tu herramienta agrega una línea de coautoría (`Co-Authored-By: ...`), déjala: es transparente con la regla 6.3. Revisa con `git log -1`. Todo se trabaja directo en `main` (no hay ramas por persona). Nunca hagas `push --force`.
- **Idioma:** conversa con el equipo en español informal. Todo lo que se entrega va en **inglés**: código, comentarios, nombres, mensajes de commit, README, textos de la interfaz, propuesta y video (el jurado es de ESPOL y de Sri Sairam, India).
- **El diseño técnico está en las secciones 11 a 16** (arquitectura, estructura de carpetas, contratos entre módulos, orden de construcción, reparto y prompts iniciales). Es una propuesta de partida: si el equipo la cambia, se actualiza ese texto. Respeta los contratos de la sección 13 para que los módulos encajen.
- **Cualquiera puede trabajar en cualquier módulo** (sección 15), siempre en `main`. Si cambias un contrato de la sección 13, avisa al equipo y actualiza este archivo.
- **Todos deben poder defender el código ante el jurado** (regla 6.4). Prefiere soluciones simples, funciones cortas y comentarios donde algo no sea obvio. Después de implementar algo no trivial, explica en 3 a 5 líneas, en español, cómo funciona.
- **Originalidad (6.2):** no copies proyectos existentes. FRESH (Flask + OSMnx + Folium para rutas en inundación) y GeoRescue (FastAPI + GeoPandas + OSMnx, proyecto de hackathon) se pueden mirar como referencia de ideas, nunca copiar código. Se citan en la propuesta.
- **Datos (6.5):** solo públicos, abiertos o sintéticos. Nada de datos personales: los reportes ciudadanos no guardan nombre ni teléfono.
- **Secretos:** tokens y claves en `.env` (ya está en `.gitignore`), nunca en el repo.

## 1. El evento

Hackathon virtual de 6 horas organizado por IEEE-HKN Nu Zeta (ESPOL) y Nu Eta (Sri Sairam, India). Equipos de 2 a 3 personas; la conformación no cambia una vez iniciado.

| Cuándo (hora Ecuador, UTC-5) | Qué |
|---|---|
| Lun 26-oct, 15h00 | Inicio. Desde aquí se puede desarrollar |
| Lun 26-oct, 21h00 | Cierre y límite de entrega. Lo que llegue después no se evalúa |
| Lun 26-oct, 22h00 | Se comunican los 3 finalistas de ESPOL |
| Mar 27-oct, 9h00–10h00 | Pitch en vivo por Google Meet. Conectarse 10 min antes, cámara encendida |

Premios solo para ESPOL: 70 USD el primer lugar y 30 USD el segundo, entre los 3 finalistas.

### Entregables (todo en inglés, antes de las 21h00)

1. **Propuesta en PDF (obligatoria):** problema, solución, tecnología, impacto esperado y plan de implementación. Debe declarar las herramientas usadas, incluida la IA, y delimitar y justificar el problema (zona, personas afectadas, alcance).
2. **Video pitch (obligatorio):** máximo 3 minutos.
3. **Repositorio (opcional):** el enlace debe abrirse sin permisos especiales o cuenta como no entregado. El historial de commits debe empezar a las 15h00 del 26-oct o después; se exceptúan plantillas y librerías de terceros declaradas (regla 6.6).

Pitch en vivo: de 5 a 7 minutos en inglés, ante 4 jurados (2 ESPOL, 2 Sri Sairam), con preguntas después.

### Tiempos sugeridos para las 6 horas

- 15h00–15h30: leer este archivo, correr `check_env.py`, decidir arquitectura y reparto, primer commit.
- 15h30–18h30: datos, mapa de riesgo, ruta, alertas.
- 18h30–19h30: simulador e integración. Ensayar el flujo de la demo completo.
- **19h30: congelar funciones.** Nada nuevo después.
- 19h30–21h00: propuesta PDF, video y entrega. Empezar el esqueleto de la propuesta antes, en paralelo. Entregar con margen (meta: 20h45).

## 2. El reto de Guayaquil

> ¿Cómo podemos desarrollar soluciones inteligentes que ayuden a Guayaquil a anticiparse y responder mejor a las lluvias intensas?

Ejes sugeridos por el comité: movilidad segura y rutas alternativas; alertas tempranas y análisis de riesgo; accesibilidad y servicios esenciales; mapas, datos y visualización; IA, predicción y optimización; soluciones inclusivas y resilientes.

## 3. Contexto local y evidencia (para la propuesta)

- **74 puntos señalizados** como vulnerables (44 por inundación, 30 por deslizamiento) por Segura EP y la ATM, con coordenadas en el geoportal de Segura EP. Sectores inundables priorizados: Ciudad de Dios, Monte Sinaí, Socio Vivienda 2, margen del Estero Salado y el norte (Urdesa Central, Miraflores, Samanes, Sauces). [ATM](https://atm.gob.ec/puntos-vulnerables-guayaquil/), [Primicias](https://www.primicias.ec/guayaquil/fenomeno-elnino-sectores-riesgo-inundaciones-albergues-seguraep-131216/)
- El Municipio proyecta acumulaciones de agua de entre 40 cm y 2,80 m en los sectores más vulnerables del noroeste, donde viven unas 500.000 personas. [Primicias](https://www.primicias.ec/guayaquil/inundaciones-fenomeno-elnino-obras-mitigacion-emapag-limpieza-canales-barrios-criticos-132895/)
- **24-oct-2026:** una tormenta dejó acumulación de agua en 68 sectores; Segura EP reportó al menos 7 arterias críticas anegadas. [Extra](https://www.extra.ec/noticia/guayaquil/tormenta-guayaquil-dejo-60-puntos-afectados-165926.html), [Primicias](https://www.primicias.ec/guayaquil/fuerte-aguacero-inundaciones-sectores-avenidas-alertas-nuevos-picos-tormenta-135671/)
- **INAMHI, advertencia meteorológica n.º 83** (25 a 28-oct-2026): lluvias de moderadas a muy intensas en Guayaquil. Umbrales citados para el Litoral: de 19 a 41 mm diarios en nivel alto, más de 42 mm en nivel muy alto. [El Universo](https://www.eluniverso.com/comunidad/ecuador/clima-en-guayaquil-manana-pronostico-de-lluvias-del-inamhi-nota/), [reproducción con umbrales](https://www.sisepuedeecuador.com/pronostico-del-tiempo-en-guayaquil-para-este-lunes-lluvias-fuertes-y-riesgo-de-inundaciones). Verificar en inamhi.gob.ec.
- **La lluvia varía por sector:** el 28-ene-2026 Mucho Lote 2 registró 92,75 mm mientras el INAMHI reportaba déficit de lluvia acumulada para la ciudad. Por eso conviene alertar por sector y no por ciudad. [Primicias](https://www.primicias.ec/guayaquil/guayaquil-deficit-lluvias-enero-2026-inamhi-114898/)
- **Lluvia + marea alta:** en marzo de 2023 una tormenta coincidió con aguaje y marea alta y colapsó el alcantarillado. Segura EP publica a diario la tabla de mareas de INOCAR. [Primicias](https://primicias.ec/noticias/sociedad/guayaquil-lluvias-inundaciones-marzo)

### Soluciones existentes y su límite

| Solución | Qué hace | Límite |
|---|---|---|
| Geoportal de Segura EP | Mapa de los puntos señalizados | Estático; sin lluvia, marea ni rutas |
| Reportes de Segura EP en redes | Avisos puntuales de acumulación de agua | Sin sistema detrás |
| Mapa de monitoreo SNGR | Amenaza por pronóstico de lluvia | Nivel cantón, no calle |
| SAT de la Prefectura del Guayas | Anticipar inundaciones hasta 72 h (con UCSG y U. de Illinois) | Provincial; en implementación en los primeros 5 cantones |
| SAT de Durán (ESPOL, 2023) | Pluviómetros y marea en 5 sectores; alertas con hasta 1 h de antelación | Solo Durán. Antecedente directo |
| Amaru (app gratuita) | Muestra rayos y marea durante tormentas | Solo vimos un fragmento; revisar funciones reales antes de compararse |
| Waze / Google Maps | Navegación | Se proponen como paliativo mientras no exista app local; un especialista notó diferencias entre su pronóstico y la lluvia real. [El Universo](https://www.eluniverso.com/comunidad/guayaquil/como-evitar-las-calles-inundadas-en-guayaquil-aplicaciones-de-movilidad-una-alternativa-ante-el-fenomeno-de-el-nino-nota/) |

**Hueco que vimos:** en nuestra búsqueda no apareció nada que combine pronóstico de lluvia, marea y riesgo del terreno con rutas a nivel de calle en Guayaquil.

## 4. Concepto elegido (el diseño técnico está en las secciones 11 a 16)

**DryGYE** (*dry* + GYE, código de Guayaquil) cubre el ciclo completo: **anticipar, orientar, aprender**.

1. **Mapa de riesgo relativo por sector**, a partir del terreno (DEM, HAND, distancia al agua) y validado contra puntos conocidos.
2. **Ruta segura:** red vial de OpenStreetMap con costos mayores en calles de riesgo, que suben con la lluvia pronosticada y la marea.
3. **Alertas por niveles** (verde, amarillo, rojo) con pronóstico de lluvia por hora y marea. Umbrales calibrables, basados en los del INAMHI.
4. **Modo simulación:** sensores virtuales con datos sintéticos que reaccionan a lluvia y marea, para que la demo no dependa de que llueva. Siempre visible como simulación.
5. **Reportes ciudadanos manuales** de calle anegada (sin datos personales) que suben el costo de esa calle.

**Fuera de alcance por ahora:** bot de Telegram (decisión del equipo; opcional para después, ver `requirements-optional.txt`), visión por computadora sobre fotos, ML predictivo, acceso a servicios esenciales (solo si sobra tiempo).

**Decisiones ya tomadas:** nombre DryGYE; datos sintéticos permitidos pero siempre declarados; la demo debe funcionar sin depender de internet en vivo.

## 5. Datos y fuentes

| Dato | Detalle | Licencia y notas |
|---|---|---|
| **DEM** | `dem_guayaquil_glo30.tif`: Copernicus GLO-30 (`COPERNICUS/DEM/GLO30` en Google Earth Engine), mosaico recortado. EPSG:4326, 1671 × 1300 px, resolución 0,000269° (~30 m), límites lon −80,150 a −79,800 y lat −2,400 a −1,950. float32, sin nodata. Valores de −2,0 a 466,8 m, media 40,0 m. | Licencia gratuita de Copernicus; incluir el aviso de atribución que exige (texto en la licencia, verificarlo antes de publicar). Es un **modelo de superficie** (incluye edificios y vegetación) y el 12,6 % de los píxeles vale 0, casi seguro agua (río, esteros, golfo); verificarlo antes de usarlo. |
| **Marea** | `GUAYAQUIL_RIO_4.pdf`: INOCAR, «Tabla II. Predicción diaria de mareas — Guayaquil (Río Guayas) 2026», octubre a diciembre. Hora local; alturas en metros sobre el nivel de referencia de INOCAR. 3 o 4 eventos por día. | Fuente oficial: citar INOCAR. Seis bloques de columnas (oct 1–16, oct 17–31, nov 1–16, nov 17–30, dic 1–16, dic 17–31); horas como `HHMM`. Pleamar y bajamar se distinguen por la altura (pleamar > 2 m). Ejemplo para validar el parseo, 26-oct: 01:45 0,80 · 06:51 4,50 · 14:15 0,55 · 19:31 4,50. Pleamares de oct–dic entre ~3,3 y ~4,7 m (las más bajas en cuadratura); en marzo–abril se han reportado de 5,1 a 5,4 m. |
| **Lluvia** | Open-Meteo: pronóstico `https://api.open-meteo.com/v1/forecast` e histórico `https://archive-api.open-meteo.com/v1/archive`. Sin clave. Centro de la ciudad: lat −2,19, lon −79,89; usar `timezone=America/Guayaquil`. | CC BY 4.0, **solo uso no comercial**, menos de 10.000 llamadas/día, 5.000/hora y 600/min. Mostrar «Weather data by Open-Meteo.com» con enlace junto a los datos. [Términos](https://open-meteo.com/en/terms). Cachear respuestas. Pendiente: probarlo desde la red del equipo. |
| **Calles** | OpenStreetMap vía `osmnx` (Overpass). | ODbL; mostrar «© OpenStreetMap contributors». Guardar el grafo en disco (GraphML) para no depender de internet en la demo. |
| **Puntos de validación** | 74 puntos de Segura EP: [geoportal](https://www.seguraep.gob.ec/index.php/geoportal/mapadeeventos). Sin confirmar si se pueden descargar; si hay que transcribirlos, citar la fuente. | Solo para validar el mapa de riesgo, no como entrada del modelo. |
| **Eventos del 24-oct-2026** | Anegados: Samanes 2 (calle Francisco de Garaycoa), calle 13 y Diez de Agosto, av. Kennedy (exteriores de Guayarte), av. Quito y Primero de Mayo, av. Don Bosco y 25 de Julio. Además Mapasingue Oeste, Florida Norte y Urdesa. | Prueba de validación del mapa y de las alertas, usando el histórico de Open-Meteo. |

Referencia opcional: NASA IMERG (lluvia satelital, ~10 km). Demasiado gruesa para sectores. Open-Meteo también ofrece una API marina y una de inundación; no se evaluaron.

## 6. Límites que hay que declarar (propuesta y pitch)

- El riesgo es **relativo**, no profundidad medida. No existen datos abiertos de sumideros, drenaje ni nivel de agua en tiempo real.
- El DEM es de superficie y de 30 m: es grueso para calles individuales.
- El modo simulación usa sensores virtuales; sus parámetros se calibran con puntos conocidos, no con mediciones. Siempre con banner «SIMULATION MODE».
- La marea es una predicción astronómica, no un nivel observado.
- Open-Meteo gratuito es solo no comercial.
- Es un prototipo. Siguiente paso: pluviómetros y sensores de nivel reales (como los del SAT de Durán) y datos de drenaje del Municipio.
- **Evitar** frases como «predice inundaciones con precisión», «evita inundaciones» o «datos en tiempo real» sin aclarar que es simulación.

## 7. Defensa ante el jurado

Pregunta probable: **«¿Y si no hay sensores?»**

> The system doesn't depend on sensors. Its baseline is the terrain risk map, built from open elevation and OpenStreetMap data, plus open rainfall forecasts and tide tables. That already gives early warnings and safer routes by sector. Sensors would make it more precise, not make it possible. Today, citizen reports fill that gap, and the same interface can take real rain gauges or water level sensors later, like the ones ESPOL already installed in Durán. In this demo we simulate them, and we label it clearly as a simulation.

En la demo, mostrar primero la parte que **no** usa sensores y después el simulador.

## 8. Entorno y flujo de trabajo

- **Instalar:** doble clic en `setup_env.bat` (Windows). Crea el entorno conda `drygye`, instala Miniconda si hace falta y al final corre `check_env.py`. Alternativas: `setup_env.ps1 -Mode venv` (sin conda) o `./setup_env.sh` (Linux/macOS). Telegram, solo si se decide: `-WithTelegram`.
- **Verificar:** `python check_env.py` (añadir `--net` para probar Open-Meteo y OpenStreetMap; `--dem ruta.tif` para revisar un DEM).
- **VS Code:** `Ctrl+Shift+P` → *Python: Select Interpreter* → entorno `drygye`.
- **Git:** primer commit a las 15h00 o después. Todos trabajan en `main`, sin ramas por persona. Commits pequeños, mensajes en inglés, `git pull --rebase` antes de `git push`, y solo se sube código que funciona (que no rompa la app ni los tests). Hacer el repo público al final para que el enlace abra sin permisos.
- **Dependencias nuevas:** agregarlas a `environment.yml` **y** a `requirements.txt`, y a la lista de la sección 9.
- **Demo:** la interfaz va en inglés, con las atribuciones de Open-Meteo, OpenStreetMap y Copernicus visibles. Cachear grafo, lluvia y marea para que funcione sin internet.

## 9. Herramientas declaradas (pegar en la propuesta)

- **Lenguaje y librerías:** Python 3.11, numpy, pandas, scipy, networkx, shapely, pyproj, geopandas, rasterio, osmnx, pysheds, matplotlib, folium, requests, pdfplumber, flask, python-dotenv, pyyaml, pytest, ipykernel. Opcional: python-telegram-bot.
- **Datos:** Copernicus DEM GLO-30, OpenStreetMap, Open-Meteo, tabla de mareas de INOCAR, advertencias del INAMHI, geoportal de Segura EP (validación).
- **IA generativa (regla 6.3):** Claude (Anthropic), en chat para investigación y planificación y con Claude Code como apoyo de programación (una persona del equipo). Las otras dos personas: completar aquí la herramienta que usen (p. ej. Codex, Copilot, Cursor). El equipo comprende y puede defender todo el proyecto.
- **Archivos previos al evento:** `CLAUDE.md`, `environment.yml`, `requirements*.txt`, `setup_env.*`, `check_env.py` y `.gitignore` son la plantilla y las librerías declaradas (regla 6.6). Confirmar con el comité, por el canal oficial de IEEE-HKN Nu Zeta que comunicó a los equipos inscritos, antes de subirlos antes de las 15h00; si no hay respuesta, el primer commit se hace a las 15h00 o después.

## 10. Pendientes por verificar

- Si INOCAR ofrece la tabla de mareas en formato descargable además del PDF.
- Si los 74 puntos de Segura EP se pueden descargar o hay que transcribirlos.
- El texto exacto del aviso de atribución de Copernicus GLO-30.
- Las funciones reales de Amaru.
- Que Open-Meteo y Overpass respondan desde la red del equipo (`python check_env.py --net`).

---

# DISEÑO TÉCNICO (propuesta de partida, 26-oct 15h00)

Supuestos: 3 personas (cada una con su asistente de IA, no necesariamente el mismo), Flask como web, Python 3.11, sin Telegram. Cada persona debe leer y entender toda esta parte antes de pedirle código a su asistente (regla 6.4).

## 11. Arquitectura

Todo corre en local, en un solo proceso Flask. Sin base de datos: archivos en `data/` y caché en `cache/`.

```
 DEM (tif) --> terrain.py --> risk.tif (riesgo base 0..1)
                                  |
 OSM --> roads.py (grafo GraphML local, riesgo por arista) <--+
                                  |
 Open-Meteo --> weather.py --+    |
 INOCAR PDF --> tides.py ----+--> alerts.py (nivel + factor dinámico)
 sensores virtuales: simulation.py -+          |
 reportes manuales: reports.py ----------------+--> routing.py (ruta rápida vs ruta segura)
                                                         |
                                       app/ (Flask + Folium/Leaflet) --> navegador
```

Flujo de una consulta de ruta: el usuario elige origen y destino -> `app` pide el estado (lluvia, marea, modo real o simulación) -> `alerts` calcula el nivel y el **factor dinámico** -> `routing` pondera cada calle con `riesgo_base * factor` + reportes -> devuelve la ruta rápida y la segura con distancia, tiempo y riesgo máximo, y el mapa las dibuja.

Riesgo base (prueba hecha sobre el DEM real, ~3 s): `risk = 0.5*(1-HAND/10 m) + 0.3*(1-dist_agua/1000 m) + 0.2*(1-pendiente/5°)`, cada término recortado a [0,1]; agua = píxeles con DEM <= 0 (verificar que cubra ríos y esteros). Resultado de la prueba: 10 % de la tierra con riesgo >= 0,6; Guasmo sur 0,63 e Isla Trinitaria 0,64 (altos); Ciudad de Dios 0,16; cerros 0,00. Es un punto de partida: los pesos se ajustan contra los puntos de validación, y hay que declarar que son una heurística.

Factor dinámico: `f = clip(0.5 + lluvia_24h/42 + 0.3*marea_alta, 0.5, 2.0)`; `risk_dyn = clip(risk_base*f + reportes, 0, 1)`; costo de arista = `largo * (1 + 10*risk_dyn)`; aristas con `risk_dyn >= 0.85` en nivel rojo se excluyen si hay alternativa. `marea_alta` = 1 si la marea en esa hora es >= 4,0 m, si no 0 (valor calibrable).

Alertas (todo en `config.py`, calibrable): verde < 19 mm/24 h; amarillo 19 a 42; rojo > 42 (umbrales INAMHI). Sube un nivel si la marea >= 4,0 m coincide con >= 10 mm en 3 h. Se calcula por sector (cuadrícula o barrio), no por ciudad.

Simulación: `simulation.py` crea de 8 a 12 sensores virtuales en puntos de riesgo alto; el nivel de cada uno acumula lluvia sintética (escenario elegido en la UI) menos drenaje, más aporte de marea; el resultado alimenta el mismo `alerts`. Todo con banner fijo «SIMULATION MODE». Escenarios: «Normal», «Heavy rain», «Heavy rain + high tide» (recrea el 24-oct).

### 11.1 MVP, límites y criterios de aceptación

**Promesa del producto:** DryGYE ayuda a comparar rutas durante lluvias intensas dentro de una zona piloto de Guayaquil, usando riesgo estimado del terreno y un escenario de lluvia y marea. En la interfaz y la propuesta, decir **«ruta de menor riesgo estimado»**, no «ruta segura»: el prototipo no confirma que una calle sea transitable ni predice inundaciones calle por calle.

**Alcance imprescindible para la demo:**

1. Elegir una sola zona piloto y un par de origen/destino que permita mostrar una diferencia entre rutas.
2. Mostrar la zona y una capa de riesgo estimado, identificada como heurística y con su resolución/fuentes.
3. Comparar una ruta rápida con una ruta de menor riesgo estimado, mostrando distancia y riesgo de cada una.
4. Incluir un escenario de lluvia intensa y marea alta. Los valores sintéticos deben llevar siempre la etiqueta «SIMULATION» y no mezclarse visualmente con datos reales.
5. Explicar qué factores modifican el riesgo y cuándo se actualizaron o de dónde provienen los datos.

**Funciones opcionales:** alertas por sector, reportes ciudadanos y varios sensores virtuales. Empezarlas solo después de integrar y probar el flujo completo de comparación de rutas. Si falta tiempo, recortarlas en ese orden.

**Reparto:** no hay responsables fijos; cualquiera puede trabajar en cualquier módulo (sección 15).

El equipo decide conjuntamente el alcance y cada persona debe poder explicar el flujo completo. No es necesario añadir aprendizaje automático: solo describir una función como IA si existe un modelo implementado, datos adecuados y una evaluación que el equipo pueda defender.

**Criterios de aceptación de la demo:**

- La app abre y muestra correctamente el mapa de la zona piloto.
- Para el origen y destino de la demo aparecen dos rutas comparables y sus métricas.
- El escenario intenso está claramente identificado; sus efectos y supuestos se pueden explicar.
- Los datos sintéticos se distinguen de los datos reales en todo momento.
- La demo puede ejecutarse con los datos guardados si falla la conexión externa.
- Al menos un integrante distinto de quien implementó cada módulo puede explicar cómo funciona.

### Estado implementado para la demo (26-oct-2026)

- Las rutas usan la red vial de OpenStreetMap de la zona piloto, guardada en `data/processed/road_graph.graphml` (solo el mayor componente conexo, para que cualquier par de puntos tenga ruta). Las líneas siguen la forma de las calles y llegan hasta los puntos elegidos. El botón «Demo trip» carga el viaje de ejemplo.
- Se pueden alternar 206 polígonos municipales de referencia de zonas inundables. Son antecedentes de estudios/eventos históricos, no cierres ni observaciones actuales. No se obtuvieron los 74 puntos vulnerables para validación.
- La ruta demo, en «Heavy rain + high tide», produjo 2.843 km / 5.7 min para la más corta y 3.163 km / 6.3 min para menor costo estimado; riesgo medio 0.702 y 0.226 respectivamente. La alternativa aún incluye un segmento muy riesgoso y la interfaz avisa.
- El parser de INOCAR generó 355 eventos para oct-dic de 2026; los cuatro eventos listados para el 26-oct coinciden con el PDF. El pronóstico conecta lluvia puntual Open-Meteo con la interpolación de marea INOCAR cuando hay cobertura temporal.
- Chequeo espacial descriptivo (muestreo cada 10 píxeles): riesgo medio 0.461 dentro de los polígonos de referencia (n=157 celdas) y 0.252 fuera (n=18.899). No es validación independiente ni precisión del modelo.
- Leaflet y sus recursos están guardados localmente; las calles, el raster, grafo y mareas permiten la demo de simulación sin internet. El fondo de teselas OpenStreetMap y el pronóstico fresco requieren internet; si faltan teselas, las capas locales siguen visibles.
- La propuesta inglesa está en `docs/DryGYE_Proposal.pdf`. El proyecto no entrena ML: datos sintéticos sirven para simular escenarios y no validan predicción real.

**Límites que deben aparecer en la propuesta y la interfaz:** el riesgo es una estimación heurística basada en datos disponibles; un DEM de aproximadamente 30 m no describe cada calle; la marea y el pronóstico no equivalen a observaciones locales de inundación; el prototipo no es una alerta oficial ni garantiza seguridad vial. No afirmar que el sistema ya evita daños o predice con precisión inundaciones.

**Ventana de implementación (15h00–21h00, hora Ecuador):** 15h00–15h25 alcance y reparto; 15h25–16h25 datos y mapa base; 16h25–17h30 capa de riesgo; 17h30–18h30 comparación de rutas; 18h30–19h00 escenario de simulación; 19h00–19h30 integración y ensayo; 19h30–20h15 propuesta PDF en inglés; 20h15–20h40 video pitch en inglés (máximo 3 minutos); 20h40–21h00 verificación de enlaces y entrega. Congelar funciones nuevas a las 19h00 para reservar tiempo para integración y entregables.

## 12. Estructura de carpetas

```
DryGYE/
  CLAUDE.md  README.md  environment.yml  requirements*.txt  setup_env.*  check_env.py  .gitignore
  data/
    raw/        dem_guayaquil_glo30.tif  GUAYAQUIL_RIO_4.pdf  validation_points.csv
    processed/  risk.tif  tides.csv  road_graph.graphml
  cache/        respuestas de Open-Meteo (ignorada por git)
  drygye/
    __init__.py  config.py
    terrain.py  tides.py  validation.py
    roads.py  routing.py  reports.py
    weather.py  alerts.py  simulation.py
  app/
    app.py  templates/index.html  static/{app.js,style.css,leaflet.js,leaflet.css,images/}
  tests/        un archivo por módulo
  scripts/      build_data.py (genera todo lo de data/processed)
  docs/         proposal/ (borrador en inglés)
```

`scripts/build_data.py` lo corre cualquiera una vez para regenerar `data/processed/`. Los archivos procesados se suben al repo (la demo no debe depender de recalcular).

## 13. Contratos entre módulos (no cambiar sin avisar al equipo)

Coordenadas siempre `(lat, lon)` en EPSG:4326. Tiempos con zona `America/Guayaquil`. Todo en `drygye/config.py`: `BBOX`, `CITY_CENTER=(-2.19,-79.89)`, rutas de archivos, umbrales, pesos, `TIDE_HIGH_M=4.0`.

- **terrain.py**
  - `build_risk_raster(dem_path, out_path) -> None` escribe `risk.tif` (float32, 0..1, NaN en agua).
  - `risk_at(lat, lon) -> float` lee `risk.tif` (carga una vez, en memoria).
  - `risk_for_points(points: list[tuple]) -> list[float]` en lote.
- **tides.py**
  - `parse_tide_pdf(pdf_path, out_csv) -> None`; `tides.csv` con columnas `datetime,height_m,kind` (`high`/`low`).
  - `tide_height_at(ts) -> float` interpola (coseno) entre eventos vecinos.
  - `is_high_tide(ts) -> bool` (altura >= `TIDE_HIGH_M`).
- **validation.py**: `validate(points_csv) -> dict` con porcentaje de puntos inundables en riesgo alto y comparación contra puntos aleatorios. `validation_points.csv`: `name,lat,lon,source,kind`.
- **roads.py**
  - `build_graph(bbox=PILOT_BBOX)` baja las calles para autos de OpenStreetMap de la zona piloto desde la API principal de OSM, en cuadros de 0,02° (Overpass suele no responder), arma el grafo con `osmnx.graph_from_xml`, conserva solo el mayor componente fuertemente conexo (toda pareja de puntos tiene ruta) y guarda en cada arista `risk_base` (promedio del riesgo del terreno a lo largo de la calle).
  - `load_graph() -> networkx.MultiDiGraph` lee `data/processed/road_graph.graphml` (si no existe, lo construye y lo guarda) y lo deja en memoria. Regenerar con internet: `python scripts/build_road_graph.py`.
  - `edge_coords(graph, u, v, data) -> [[lat, lon], ...]` forma real de la calle.
- **routing.py**
  - `compare_routes(origin, destination, state) -> {"fast": ..., "safe": ..., "alternatives": [...], "snapping": {"origin_m", "destination_m"}, "warning": str|None}`. Las alternativas (hasta 2) salen del método de penalización: se encarecen las calles de las rutas ya encontradas y se busca otra vez; se descartan las que comparten más del 70 % del recorrido; `state` viene de `alerts` (usa `level` y `factor`).
  - Cada ruta: `{"coords": [[lat,lon],...], "length_m", "time_min", "mean_risk", "max_risk"}`. `coords` empieza y termina en los puntos que eligió el usuario y sigue la forma de las calles.
- **reports.py**: `add_report(lat, lon, note="") -> dict`, `active_reports() -> list[dict]`, caducan a las 3 h; persistencia en `data/reports.json` (sin datos personales).
- **weather.py**
  - `get_forecast(force_refresh=False) -> dict` con series horarias de precipitación, probabilidad y temperatura para el punto central de Guayaquil; usa caché de 60 min y caché anterior si falla la red.
  - `forecast_summary(data) -> dict` devuelve acumulados de 3/24 h y las próximas 12 horas para la interfaz.
- **alerts.py**
  - `current_state(scenario) -> dict` calcula alertas para un escenario sintético de lluvia y marea.
  - `forecast_state(rain_24h, tide_m=None) -> dict` calcula alertas y el factor de ruta con lluvia puntual y marea opcional de INOCAR.
  - `sector_levels(state) -> list[dict]`.
- **simulation.py**: `SCENARIOS`, `simulate(scenario, minutes) -> dict` (serie de lluvia sintética y nivel por sensor virtual), `virtual_sensors() -> list[dict]`.
- **app (C + B)**: rutas Flask `GET /` (mapa), `GET /api/state?mode=simulation|forecast&scenario=`, `GET /api/weather` (pronóstico horario), `GET /api/risk`, `GET /api/reference/roads`, `GET /api/reference/flood-zones`, `GET /api/route?from=lat,lon&to=lat,lon&mode=simulation|forecast&scenario=`. Los recursos Leaflet se sirven localmente; las teselas de fondo son externas. JSON en inglés. En modo forecast, lluvia puntual y marea INOCAR (si la tabla cubre la hora) modifican el factor de ruta.

## 14. Orden de construcción (hitos con hora)

1. **15h00–15h30** — Todos: leer este archivo, `python check_env.py`, crear `config.py`, primer commit en `main` con la plantilla y `data/raw/`.
2. **15h30–16h30 (Hito 1)** — Datos y riesgo: `risk.tif` y `tides.csv` listos y subidos. Calles y rutas: grafo en caché y ruta rápida vs ruta con riesgo ficticio constante. Alertas y web: esqueleto Flask con mapa base y `/api/state` con valores de prueba. Todo queda integrado en `main`.
3. **16h30–18h00 (Hito 2)** — Datos y riesgo: validación contra los puntos y ajuste de pesos. Calles y rutas: riesgo por arista desde `risk.tif`, `compare()` y reportes. Alertas y web: Open-Meteo con caché, `alerts`, mapa con capa de riesgo y selector de ruta.
4. **18h00–19h00 (Hito 3)** — Alertas y web: simulación, escenarios y banner. Calles y rutas: ruta en el mapa con rápida vs segura. Datos y riesgo: número de validación y tabla de límites para la propuesta; inicia el borrador del PDF.
5. **19h00–19h30** — Integración, ensayo de la demo completa sin internet (apagar el wifi y probar). **19h30: congelar funciones.**
6. **19h30–20h45** — Propuesta PDF en inglés, video de 3 min, README, repo público, entrega.

Si algo se atrasa, se recorta en este orden: reportes ciudadanos, sectores en alertas, escenarios extra. Lo que nunca se recorta: mapa de riesgo, ruta rápida vs segura, alertas, simulación etiquetada.

## 15. Organización del equipo

No hay reparto fijo por persona: cualquiera puede trabajar en cualquier módulo. Para no pisarse, avisar en el chat del equipo qué archivo se está editando antes de empezar y hacer commits chicos.

Reglas de git: todos trabajan directo en `main`, sin ramas por persona ni PRs. Commits chicos y frecuentes (al menos al cumplir cada hito); `git pull --rebase` antes de cada `git push` y, si hay conflicto, se resuelve con quien editó ese archivo; nunca `push --force`. Si se cambia un contrato de la sección 13 o `config.py`, avisar al equipo y actualizar este archivo. Si alguien se atasca en algo, se le pasa a quien termine primero.

## 16. Prompts iniciales (quien tome una tarea pega su prompt en su asistente, con este archivo ya abierto o pegado)

**Todos, primero:** «Lee CLAUDE.md completo. Corre `python check_env.py` y dime si el entorno está bien. Crea `drygye/config.py` según la sección 13 con BBOX del DEM, rutas de archivos y umbrales (solo constantes). Después espera mi siguiente instrucción.»

**Datos y riesgo:** «Trabajo en `main`. Implementa `drygye/terrain.py` según el contrato de la sección 13: calcula HAND con pysheds (o, si tarda mucho, la diferencia de altura al agua más cercana con `scipy.ndimage.distance_transform_edt`), distancia al agua y pendiente, y combina con la fórmula de la sección 11. Agua = DEM <= 0. Escribe `data/processed/risk.tif`. Añade `tests/test_terrain.py` con un DEM sintético pequeño. Luego `tides.py`: parsear `data/raw/GUAYAQUIL_RIO_4.pdf` con pdfplumber (ver sección 5 para el formato y el ejemplo del 26-oct como prueba) a `tides.csv`. Explícame en 3 a 5 líneas cómo funciona cada cosa, porque debo defenderla.»

**Calles y rutas:** «Trabajo en `main`. Implementa `drygye/roads.py`: baja con OSMnx el grafo de calles transitables para autos dentro de BBOX (si es muy grande, usa los 5 distritos centrales y norte primero), guárdalo en GraphML en `data/processed/` y cárgalo desde disco. Luego `routing.py` con `route()` y `compare()` según la sección 13 y la fórmula de costo de la sección 11; mientras no exista `risk.tif`, usa un riesgo falso aleatorio por arista con una bandera clara en el código. Añade tests con un grafo pequeño de networkx. Después `reports.py`. Explícame cómo funciona cada cosa.»

**Alertas, simulación y web:** «Trabajo en `main`. Crea la app Flask de la sección 13 con un mapa Leaflet (usa folium solo si ayuda), `/api/state` con valores de prueba al inicio, selector de modo «real/simulation» y de escenario, y un banner fijo «SIMULATION MODE» cuando aplique. Pie de página con las atribuciones: «Weather data by Open-Meteo.com», «© OpenStreetMap contributors», Copernicus DEM. Luego `weather.py` con Open-Meteo, caché en disco y plan B offline, y `alerts.py` con los umbrales de la sección 11. Interfaz en inglés. Explícame cómo funciona cada cosa.»

## 17. Antes de entregar

- Probar la demo sin internet y con el escenario «Heavy rain + high tide».
- Que `README.md` tenga: qué es, cómo instalar (`setup_env.bat`), cómo correr la app, datos y atribuciones, límites (sección 6) y herramientas declaradas (sección 9).
- Repo público, probado en una ventana de incógnito.
- Cada persona puede explicar el flujo completo y cualquier módulo.
