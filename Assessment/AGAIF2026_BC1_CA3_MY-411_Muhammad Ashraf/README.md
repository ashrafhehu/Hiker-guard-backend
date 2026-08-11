# ASEAN GeoAI Interactive Web Map Explorer (Assignment 3)

**Participant Name:** Muhammad Ashraf  
**Participant Reference Code:** MY-411  
**Course:** ASEAN GeoAI Fusion 2026 Hackathon  
**Assignment:** Certified Assessment Assignment 3 — AI-Assisted Interactive Web Mapping Using Leaflet.js  

---

## 🌟 Application Overview

The **ASEAN GeoAI Interactive Web Map Explorer** is a modern, responsive, web-based geospatial visualization application built using **Leaflet.js**, **HTML5**, **CSS3**, and **JavaScript**. It renders 10 ASEAN member country polygon boundaries and 230 municipal places/cities extracted from the official `ASEAN Shp Data` dataset.

### key Features:
- 🗺 **Multiple Base Map Layers:** Switch between OpenStreetMap Standard, CartoDB Positron (Light), CartoDB Dark Matter, and Esri World Imagery Satellite maps.
- 📍 **Point Feature Representation:** 230 municipal settlements styled as circle markers, categorized and color-coded by settlement type (Capitals, Cities, Towns).
- 🚩 **Country Boundaries Layer:** 10 ASEAN member nation polygons with hover highlight effects and interactive tooltips.
- 💬 **Interactive HTML Popups:** Displays city name, country name, country flag, settlement type, population, and latitude/longitude coordinates.
- 🔍 **Real-Time Search & Filtering:** Filter places instantly by place name search, country dropdown, or settlement type.
- 📐 **Automatic Extent Fitting & Extent Reset:** Automatically fits the initial view to the data extent (`map.fitBounds()`) and resets views with one click.
- 💻 **100% Offline & Standalone Compatible:** Uses bundled standalone Leaflet libraries (`lib/leaflet.js`) and embedded GeoJSON (`data/asean_data.js`) to guarantee execution in any browser without CORS or SSL CDN blockages.

---

## 📁 Directory Structure

```text
AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf/
├── index.html                      # Main HTML structure & UI layout
├── style.css                       # Application stylesheet (Dark Glassmorphism theme)
├── script.js                      # Application logic, Leaflet map setup & filters
├── README.md                       # Instruction manual (this file)
├── AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf_Report.pdf  # Comprehensive PDF Assignment Report
├── lib/                            # Standalone Leaflet library & assets
│   ├── leaflet.js
│   ├── leaflet.css
│   └── images/
├── data/                           # Geospatial datasets
│   ├── asean_countries.geojson
│   ├── asean_places.geojson
│   ├── asean_data.js
│   └── Place.xlsx
└── screenshots/                    # High-resolution application screenshots
    ├── map_overview.png
    ├── map_filter_search.png
    └── map_popup_detail.png
```

---

## 🚀 How to Launch and Use the Application

1. **Unzip the Submission File:**
   Extract `AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf.zip` to your local folder.

2. **Open the Application:**
   Double-click `index.html` or right-click `index.html` and choose **Open with Google Chrome**, **Microsoft Edge**, or **Mozilla Firefox**. No local web server or internet connection is strictly required!

3. **Interacting with the Map:**
   - **Pan & Zoom:** Use your mouse scroll wheel, touch gestures, or the `+` / `-` buttons on the top left of the map.
   - **Click Places:** Click any colored circle marker to open an attribute popup detailing the place's name, country flag, settlement type, population, and coordinates.
   - **Hover Country Boundaries:** Move your mouse over any country polygon to see a highlighted border and country name tooltip.
   - **Search & Filter:** Use the left sidebar search bar to type a city name (e.g., *Kuala Lumpur*, *Jakarta*, *Penang*), or select a specific ASEAN country from the dropdown menu.
   - **Layer Control:** Hover over the layer icon on the top-right of the map to toggle base map styles (Dark, Light, OSM, Satellite) or toggle boundary/place layers.

---

## 📜 Attribution & Data Sources

- **Leaflet.js:** Open-source JavaScript library for mobile-friendly interactive maps (&copy; Vladimir Agafonkin).
- **Base Map Tiles:** &copy; [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, [CARTO](https://carto.com/), and [Esri](https://www.esri.com/).
- **Geospatial Data:** ASEAN Place & Country Shapefiles provided by the ASEAN GeoAI Fusion 2026 Secretariat.
