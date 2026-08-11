/* ==========================================================================
   ASEAN GeoAI Interactive Web Map - Application Logic (script.js)
   Participant: Muhammad Ashraf (MY-411)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  
  // ------------------------------------------------------------------------
  // 1. Initial Data Validation & Fallbacks
  // ------------------------------------------------------------------------
  const countriesData = window.ASEAN_COUNTRIES || { type: "FeatureCollection", features: [] };
  const placesData = window.ASEAN_PLACES || { type: "FeatureCollection", features: [] };

  console.log(`Loaded ${countriesData.features.length} countries and ${placesData.features.length} places.`);

  // ------------------------------------------------------------------------
  // 2. Base Map Tile Layers Definition
  // ------------------------------------------------------------------------
  const osmStandard = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  });

  const cartoPositron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
  });

  const cartoDark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    subdomains: 'abcd',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
  });

  const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 18,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
  });

  // Offline Blank Grid Canvas Layer (Dummy layer for offline execution)
  const offlineVectorGrid = L.layerGroup();

  // ------------------------------------------------------------------------
  // 3. Initialize Leaflet Map Instance
  // ------------------------------------------------------------------------
  const map = L.map('map', {
    center: [4.2105, 101.9758], // Centered on Peninsular & East Malaysia / ASEAN core
    zoom: 5,
    layers: [osmStandard, offlineVectorGrid], // Default OSM Standard basemap
    zoomControl: true
  });

  // Critical fix for flexbox container sizing
  setTimeout(() => {
    map.invalidateSize();
  }, 200);

  const baseMaps = {
    "OpenStreetMap Standard": osmStandard,
    "CartoDB Positron (Light)": cartoPositron,
    "CartoDB Dark Matter": cartoDark,
    "Esri Satellite Imagery": esriSatellite,
    "Offline Tactical Vector Grid": offlineVectorGrid
  };

  // ------------------------------------------------------------------------
  // 4. Country Boundary Polygon Layer Styling & Interaction
  // ------------------------------------------------------------------------
  function getCountryColor(countryName) {
    const colorMap = {
      'Malaysia': '#3b82f6',
      'Indonesia': '#ef4444',
      'Thailand': '#f59e0b',
      'Vietnam': '#10b981',
      'Philippines': '#8b5cf6',
      'Singapore': '#06b6d4',
      'Brunei Darussalam': '#ec4899',
      'Cambodia': '#f97316',
      'Laos DR': '#14b8a6',
      'Myanmar': '#6366f1'
    };
    return colorMap[countryName] || '#64748b';
  }

  function styleCountryFeature(feature) {
    const cName = feature.properties ? feature.properties.Country : '';
    return {
      fillColor: getCountryColor(cName),
      weight: 2.0,
      opacity: 0.9,
      color: '#94a3b8',
      dashArray: '4',
      fillOpacity: 0.45 // Rich opacity for bold country rendering
    };
  }

  function highlightCountry(e) {
    const layer = e.target;
    layer.setStyle({
      weight: 3.0,
      color: '#ffffff',
      dashArray: '',
      fillOpacity: 0.65
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
      layer.bringToFront();
    }
  }

  function resetCountryHighlight(e) {
    countriesLayer.resetStyle(e.target);
  }

  const countriesLayer = L.geoJSON(countriesData, {
    style: styleCountryFeature,
    onEachFeature: (feature, layer) => {
      const cName = feature.properties ? feature.properties.Country : 'ASEAN Nation';
      
      // Bind Tooltip on hover
      layer.bindTooltip(`<strong>${cName}</strong>`, {
        sticky: true,
        direction: 'auto',
        className: 'country-tooltip'
      });

      layer.on({
        mouseover: highlightCountry,
        mouseout: resetCountryHighlight
      });
    }
  }).addTo(map);

  // ------------------------------------------------------------------------
  // 5. Place Point Feature Layer & Popup Styling
  // ------------------------------------------------------------------------
  function getMarkerStyle(feature) {
    const pType = (feature.properties.type || '').toLowerCase();
    let fillColor = '#10b981'; // Green for default town/other
    let radius = 6;

    if (pType.includes('capital') || feature.properties.population > 1000000) {
      fillColor = '#ef4444'; // Red for capital/mega city
      radius = 9;
    } else if (pType.includes('city')) {
      fillColor = '#3b82f6'; // Blue for city
      radius = 7;
    }

    return {
      radius: radius,
      fillColor: fillColor,
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.9
    };
  }

  function formatPopulation(pop) {
    if (!pop || pop === 0 || pop === '0') {
      return 'Data Not Recorded';
    }
    return Number(pop).toLocaleString();
  }

  function createPopupContent(properties) {
    const pName = properties.name || 'Unnamed Place';
    const cName = properties.Country || 'ASEAN';
    const pType = properties.type || 'Municipal Settlement';
    const popStr = formatPopulation(properties.population);
    const lat = properties.Lat ? Number(properties.Lat).toFixed(4) : 'N/A';
    const lng = properties.Long ? Number(properties.Long).toFixed(4) : 'N/A';
    const flagUrl = properties.flag || '';

    const flagImgHtml = flagUrl ? `<img src="${flagUrl}" class="popup-flag" alt="${cName} Flag" onerror="this.style.display='none'">` : '';

    return `
      <div class="popup-container">
        <div class="popup-header">
          ${flagImgHtml}
          <div class="popup-title">
            <h4>${pName}</h4>
            <span>${cName}</span>
          </div>
        </div>
        <div class="popup-body">
          <div class="popup-row">
            <span class="popup-label">Settlement Type:</span>
            <span class="popup-value badge-type">${pType}</span>
          </div>
          <div class="popup-row">
            <span class="popup-label">Population:</span>
            <span class="popup-value">${popStr}</span>
          </div>
          <div class="popup-row">
            <span class="popup-label">Coordinates:</span>
            <span class="popup-value">${lat}&deg;, ${lng}&deg;</span>
          </div>
        </div>
      </div>
    `;
  }

  let placesLayer = null;

  function renderPlacesLayer(filteredGeoJSON) {
    if (placesLayer) {
      map.removeLayer(placesLayer);
    }

    placesLayer = L.geoJSON(filteredGeoJSON, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, getMarkerStyle(feature));
      },
      onEachFeature: (feature, layer) => {
        layer.bindPopup(createPopupContent(feature.properties));
        
        layer.on('mouseover', function () {
          this.setStyle({ weight: 3, fillOpacity: 1 });
        });
        layer.on('mouseout', function () {
          this.setStyle(getMarkerStyle(feature));
        });
      }
    }).addTo(map);

    // Update Counter
    document.getElementById('stat-visible-places').innerText = filteredGeoJSON.features.length;
  }

  // Initial Places Render
  renderPlacesLayer(placesData);

  // Add Overlay Layer Control
  const overlayMaps = {
    "ASEAN Country Boundaries": countriesLayer,
    "ASEAN Municipal Places": placesLayer
  };
  L.control.layers(baseMaps, overlayMaps, { position: 'topright' }).addTo(map);

  // Expose global helper to trigger popup for testing/screenshots
  window.openPlacePopup = function(placeName) {
    if (!placesLayer) return;
    placesLayer.eachLayer(layer => {
      if (layer.feature && layer.feature.properties && layer.feature.properties.name === placeName) {
        map.setView(layer.getLatLng(), 8);
        layer.openPopup();
      }
    });
  };

  // ------------------------------------------------------------------------
  // 6. Populate Filter Dropdowns dynamically
  // ------------------------------------------------------------------------
  const countrySelect = document.getElementById('country-select');
  const typeSelect = document.getElementById('type-select');

  const uniqueCountries = new Set();
  const uniqueTypes = new Set();

  placesData.features.forEach(f => {
    if (f.properties.Country) uniqueCountries.add(f.properties.Country);
    if (f.properties.type) uniqueTypes.add(f.properties.type);
  });

  Array.from(uniqueCountries).sort().forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.innerText = c;
    countrySelect.appendChild(opt);
  });

  Array.from(uniqueTypes).sort().forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.innerText = t.charAt(0).toUpperCase() + t.slice(1);
    typeSelect.appendChild(opt);
  });

  // Update Stats
  document.getElementById('stat-total-places').innerText = placesData.features.length;
  document.getElementById('stat-total-countries').innerText = uniqueCountries.size;

  // ------------------------------------------------------------------------
  // 7. Filtering & Real-time Search Logic
  // ------------------------------------------------------------------------
  const searchInput = document.getElementById('search-input');
  const clearSearchBtn = document.getElementById('clear-search-btn');

  function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const selectedCountry = countrySelect.value;
    const selectedType = typeSelect.value;

    clearSearchBtn.style.display = searchTerm ? 'block' : 'none';

    const filteredFeatures = placesData.features.filter(f => {
      const pName = (f.properties.name || '').toLowerCase();
      const cName = f.properties.Country || '';
      const pType = f.properties.type || '';

      const matchesSearch = !searchTerm || pName.includes(searchTerm);
      const matchesCountry = selectedCountry === 'ALL' || cName === selectedCountry;
      const matchesType = selectedType === 'ALL' || pType === selectedType;

      return matchesSearch && matchesCountry && matchesType;
    });

    const filteredGeoJSON = {
      type: "FeatureCollection",
      features: filteredFeatures
    };

    renderPlacesLayer(filteredGeoJSON);

    // Auto fit bounds if filtered results exist
    if (filteredFeatures.length > 0) {
      const tempLayer = L.geoJSON(filteredGeoJSON);
      map.fitBounds(tempLayer.getBounds(), { padding: [40, 40], maxZoom: 10 });
    }
  }

  // Event Listeners
  searchInput.addEventListener('input', applyFilters);
  countrySelect.addEventListener('change', applyFilters);
  typeSelect.addEventListener('change', applyFilters);

  clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    applyFilters();
  });

  document.getElementById('reset-bounds-btn').addEventListener('click', () => {
    if (placesLayer && placesLayer.getLayers().length > 0) {
      map.fitBounds(placesLayer.getBounds(), { padding: [30, 30] });
    } else {
      map.fitBounds(countriesLayer.getBounds(), { padding: [30, 30] });
    }
  });

  document.getElementById('reset-filters-btn').addEventListener('click', () => {
    searchInput.value = '';
    countrySelect.value = 'ALL';
    typeSelect.value = 'ALL';
    applyFilters();
    map.fitBounds(placesLayer.getBounds(), { padding: [30, 30] });
  });

  // Fit Map Bounds initially to display full ASEAN region
  if (placesLayer && placesLayer.getLayers().length > 0) {
    map.fitBounds(placesLayer.getBounds(), { padding: [30, 30] });
  }

  setTimeout(() => {
    map.invalidateSize();
    if (placesLayer && placesLayer.getLayers().length > 0) {
      map.fitBounds(placesLayer.getBounds(), { padding: [30, 30] });
    }
  }, 500);

});
