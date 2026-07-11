# Smart Irrigation Scheduling Platform — FAO-56

A professional **Decision Support System (DSS)** that computes crop water
requirements and daily irrigation schedules using the **FAO Irrigation &
Drainage Paper No. 56** methodology and the **FAO Penman-Monteith** equation.

Built for farmers, agronomists, irrigation consultants and researchers. The
calculation engine is validated against the reference *"Irrigation Schedule
program"* Riyadh workbook and against the FAO-56 paper itself.

---

## Quick start (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File run.ps1
```

The first run installs dependencies, builds the web UI, and opens
<http://127.0.0.1:8000>. Later runs start instantly. Use `-Rebuild` to force a
fresh UI build, `-Port 9000` to change the port.

A **"Load Sample Project"** button pre-fills a full Jazan/Riyadh demo (Tomato,
Sandy Loam, drip @ 90 %) with a **real year of daily Riyadh climate** and runs
the whole schedule so you can see the system working immediately.

---

## Architecture

```
IRR2/
├── backend/                 FastAPI + SQLAlchemy (SQLite)
│   ├── app/
│   │   ├── engine/          Pure, unit-tested FAO-56 calculation engine
│   │   │   ├── eto.py         Penman-Monteith ETo + radiation block
│   │   │   ├── kc.py          Crop coefficient & growth-stage curve
│   │   │   ├── soil.py        TAW / RAW (available water)
│   │   │   ├── salinity.py    Leaching requirement
│   │   │   ├── rainfall.py    Effective rainfall (USDA-SCS / FAO / fixed)
│   │   │   ├── irrigation.py  Depth, volume, runtime
│   │   │   └── scheduler.py   Daily soil-water balance + irrigation trigger
│   │   ├── models.py        ORM tables (Crops, Soils, Systems, Projects, Climate)
│   │   ├── seed_data.py     60 crops + 12 soils + 8 systems (FAO-56 defaults)
│   │   ├── routers/         REST API (catalog, projects, climate, scheduling, reports)
│   │   └── main.py          App entry — serves API + built UI
│   ├── data/                SQLite DB + riyadh_climate.json
│   └── tests/               pytest suite (engine validation)
└── frontend/                React + Vite + TypeScript (EN / AR, RTL)
    └── src/pages/           Dashboard, Projects, Climate, Schedule, Calendar, Reports, Crops
```

The **calculation engine is fully decoupled** from the UI and database
(spec §36) and can be imported and unit-tested on its own.

---

## The FAO-56 engine

Reference ET (ETo) uses the canonical Penman-Monteith form (FAO-56 Eq. 6):

```
        0.408·Δ·(Rn − G) + γ·(900/(T+273))·u₂·(es − ea)
ETo = ────────────────────────────────────────────────
                 Δ + γ·(1 + 0.34·u₂)
```

All intermediate variables (Δ, γ, es, ea, Ra, Rso, Rns, Rnl, Rn, u₂, …) are
computed from FAO-56 and are viewable per day via **Show Calculation Details**.

The daily schedule then applies:

| Step | Formula | Ref |
|------|---------|-----|
| Crop ET | `ETc = Kc · ETo` | §12 |
| Available water | `TAW = 1000·(θFC − θWP)·Zr` | §10 |
| Readily available | `RAW = p·TAW`, `p = p_table + 0.04·(5 − ETc)` | §11 |
| Water balance | `Dr,i = Dr,i-1 − Pe − I + ETc + DP` | §14 |
| Trigger | irrigate when `Dr ≥ RAW` | §15 |
| Gross depth | `Dg = Dn / ((1 − LR)·Ea)` | §17 |
| Leaching | `LR = ECw / (5·ECe − ECw)` | §18 |
| Volume | `V(m³) = Dg(mm)·Area(m²)/1000` | §19 |
| Runtime | `t = V / (n·q_emitter)` | §20 |

### Validation & a note on the reference workbook

The engine reproduces the reference Riyadh workbook's vapour-pressure, slope,
psychrometric and wind terms **exactly**. Two formula bugs were found in that
workbook and are **not** replicated here (the engine follows the FAO-56 paper):

1. **Extraterrestrial radiation Ra** — the workbook multiplies the inverse
   Earth-Sun distance `dr` onto only the first bracket term of FAO-56 Eq. 21;
   the correct formula applies `dr` to the whole bracket. This inflates the
   workbook's Ra/ETo by ~8-9 %.
2. **Penman-Monteith denominator** — rows after the first use `(T + 237)`
   instead of the correct `(T + 273)`.

Run the test suite:

```powershell
cd backend
python -m pytest -q
```

---

## Data entry

Climate can be entered three ways (spec §4):

* **Manual / bulk** via the API.
* **CSV / Excel upload** — columns auto-detected (Date, Tmax, Tmin, RHmax,
  RHmin, RHmean, Wind, Rs/Solar, Sunshine, Rainfall). Missing solar radiation
  is estimated from sunshine hours (FAO-56 Eq. 35).
* Every default value (crop Kc, soil FC/WP, efficiency, …) is **user-editable**
  (spec §37).

## Reports

* **Excel** (`.xlsx`) — a Summary sheet + the full daily schedule.
* **CSV** — the daily schedule table.

---

## Authentication

The app is protected by a username/password login. A default admin user is
created on first boot:

| | |
|--|--|
| Username | `admin` |
| Password | `admin123` |

**Change these in production** via environment variables `ADMIN_USERNAME` and
`ADMIN_PASSWORD` (applied when the database is first seeded), and set a stable
`SECRET_KEY` so login tokens survive restarts. Change the password after login
via the API `POST /api/auth/change-password`.

## Weather data (NASA POWER & Open-Meteo)

On the **Climate Data** page you can auto-fill a project's daily climate from:

* **NASA POWER** — global historical daily data (T2M, RH2M, WS2M @2 m,
  ALLSKY_SFC_SW_DWN, precipitation). Units are read from the response and solar
  is converted to MJ/m²/day.
* **Open-Meteo** (ERA5 archive) — temperature, precipitation, 10 m wind
  (converted to 2 m via FAO-56 Eq. 47), shortwave radiation (MJ/m²), and hourly
  humidity aggregated to daily max/min.

Coordinates come from the selected **city** (a built-in database of ~95 Saudi
cities across all 13 regions, each with latitude/longitude/elevation). Leave the
date range empty to fetch the crop's whole growing season automatically.

## Reports

* **PDF** — a formatted one-page engineering report (reportlab).
* **Excel** — Summary sheet + full daily schedule.
* **CSV** — the daily schedule table.

## Deploy to Render

This repo ships a **Dockerfile** (multi-stage: Node builds the UI, Python serves
it) and a **`render.yaml`** blueprint.

1. Push this repo to GitHub (already done if you're reading it there).
2. In [Render](https://render.com): **New +** → **Blueprint** → connect the repo.
   Render reads `render.yaml` and builds the Docker image automatically.
   *(Or: **New +** → **Web Service** → **Docker** runtime, no build/start command
   needed — the Dockerfile handles everything.)*
3. Open the generated `*.onrender.com` URL. The database auto-seeds catalogs and
   the demo project on first boot.

**Note on data:** the app uses SQLite. On Render's free tier the disk is
**ephemeral** — catalogs and the demo project re-seed on every deploy, but
user-created projects reset. To persist them, attach a **Render Disk** and set
the `DATA_DIR` environment variable to its mount path (e.g. `/data`).

## Tech stack

| Layer | Technology |
|-------|-----------|
| Engine / API | Python 3.12, FastAPI, SQLAlchemy 2, SQLite |
| Frontend | React 18, Vite 6, TypeScript, Chart.js |
| Languages | English + Arabic (RTL) |

Reference model author of the Riyadh workbook: *Eng. Mohammed Elsiddig A. Abass*.
