/**
 * FloodGuard Nilgiris Disaster Intelligence — Evidence & Susceptibility Workspace
 * Spatial Positive-Unlabeled (PU) XGBoost Model & Rainfall Scenario Simulation
 * Strict Scientific Governance: Demonstration spatial susceptibility, not live forecasts.
 */
(() => {
  "use strict";

  // DOM Helpers
  const $ = id => document.getElementById(id);
  const escapeHtml = val => {
    if (val === null || val === undefined) return "—";
    const div = document.createElement("div");
    div.textContent = String(val);
    return div.innerHTML;
  };

  const fmt = (val, decimals = 1) => {
    if (val === "" || val === null || val === undefined || isNaN(Number(val))) return "—";
    return Number(val).toFixed(decimals);
  };

  const api = async path => {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`HTTP ${res.status} (${res.statusText})`);
    return res.json();
  };

  // State
  let map;
  let eventLayer;
  let boundaryLayer;
  let centroidLayer;
  let allEvents = [];
  let scenarioRecords = [];
  let activeScenarioMeta = null;
  let villagePolygonsMap = new Map();
  let selectedVillageLgd = null;
  let currentTierFilter = "all";
  let currentSearchTerm = "";
  let sliderDebounceTimer = null;

  /**
   * Determine Tier classification for demonstration display
   * High: >= 60.0 | Medium: 30.0 - 59.9 | Low: < 30.0
   */
  function getTierInfo(score) {
    const num = Number(score);
    if (num >= 60.0) {
      return { tier: "HIGH", className: "tier-high", label: "HIGH", color: "#f43f5e", stroke: "#f87171", fillOpacity: 0.22 };
    } else if (num >= 30.0) {
      return { tier: "MEDIUM", className: "tier-medium", label: "MED", color: "#f59e0b", stroke: "#fbbf24", fillOpacity: 0.16 };
    } else {
      return { tier: "LOW", className: "tier-low", label: "LOW", color: "#10b981", stroke: "#34d399", fillOpacity: 0.12 };
    }
  }

  /**
   * Format delta chip
   */
  function formatDelta(delta) {
    const num = Number(delta || 0);
    if (Math.abs(num) < 0.05) {
      return { text: "Δ 0.0", className: "delta-zero" };
    } else if (num > 0) {
      return { text: `Δ +${num.toFixed(1)}`, className: "delta-pos" };
    } else {
      return { text: `Δ ${num.toFixed(1)}`, className: "delta-neg" };
    }
  }

  /**
   * Initialize Leaflet Situation Map
   */
  function initMap() {
    map = L.map("map", {
      center: [11.41, 76.69],
      zoom: 10,
      zoomControl: true,
      attributionControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "© <a href='https://www.openstreetmap.org/copyright' target='_blank'>OpenStreetMap</a> contributors"
    }).addTo(map);

    boundaryLayer = L.layerGroup().addTo(map);
    eventLayer = L.layerGroup().addTo(map);
    centroidLayer = L.layerGroup().addTo(map);

    // Layer Toggles
    const toggleEvents = $("toggle-events");
    if (toggleEvents) {
      toggleEvents.onchange = e => e.target.checked ? map.addLayer(eventLayer) : map.removeLayer(eventLayer);
    }
    const toggleBoundaries = $("toggle-boundaries");
    if (toggleBoundaries) {
      toggleBoundaries.onchange = e => e.target.checked ? map.addLayer(boundaryLayer) : map.removeLayer(boundaryLayer);
    }
    const toggleCentroids = $("toggle-centroids");
    if (toggleCentroids) {
      toggleCentroids.onchange = e => e.target.checked ? map.addLayer(centroidLayer) : map.removeLayer(centroidLayer);
    }

    // Reset View Button
    const btnReset = $("btn-reset-map");
    if (btnReset) {
      btnReset.onclick = () => {
        map.flyTo([11.41, 76.69], 10, { duration: 0.8 });
      };
    }
  }

  /**
   * Load System & Governance Status
   */
  async function loadStatus() {
    try {
      const data = await api("/api/status");
      const statusEl = $("model-status");
      const reasonEl = $("model-reason");
      if (statusEl) {
        statusEl.textContent = `PU XGBoost (LOTO ${fmt(data.loto_roc_auc, 3)})`;
      }
      if (reasonEl) {
        reasonEl.textContent = `PU-ML Active · 25 Positive · 15 Unlabeled · 6-Fold LOTO CV (ROC-AUC ${fmt(data.loto_roc_auc, 4)})`;
      }
    } catch (err) {
      console.warn("Status fetch failed:", err);
    }
  }

  /**
   * Load Administrative Framework & Reconciliation
   */
  async function loadVillages() {
    const data = await api("/api/villages?limit=102");
    
    const summaryEl = $("village-summary");
    if (summaryEl) {
      summaryEl.textContent = `${data.record_count} Village Master administrative records; ${data.exact_spatial_matches} exact LGD polygon matches. ${data.village_master_only} Master-only and ${data.kmz_only} KMZ-only records remain unmatched.`;
    }

    const tableEl = $("village-table");
    if (tableEl) {
      tableEl.innerHTML = data.records.slice(0, 15).map(row => `
        <tr>
          <td>${escapeHtml(row.village_name_en)}</td>
          <td>${escapeHtml(row.taluk_name_en)}</td>
          <td class="mono">${escapeHtml(row.village_lgd_code)}</td>
        </tr>
      `).join("");
    }
  }

  /**
   * Load GSI / NLFC Landslide Event Inventory
   */
  async function loadEvents() {
    const data = await api("/api/events");
    allEvents = data.records || [];
    
    const totalEl = $("event-total");
    if (totalEl) totalEl.textContent = data.record_count;

    const datesDl = $("event-dates");
    if (datesDl && data.date_categories) {
      datesDl.innerHTML = Object.entries(data.date_categories).map(([k, v]) => `
        <div>
          <dt>${escapeHtml(k.replace(/_/g, " ").toUpperCase())}</dt>
          <dd>${v}</dd>
        </div>
      `).join("");
    }

    const tableEl = $("events-table");
    if (tableEl) {
      tableEl.innerHTML = allEvents.slice(0, 15).map(row => `
        <tr>
          <td>${escapeHtml(row.location_description)}</td>
          <td class="mono">${escapeHtml(row.history_raw)}</td>
          <td>${escapeHtml(row.material_involved)}</td>
          <td>${escapeHtml(row.movement_type)}</td>
        </tr>
      `).join("");
    }

    // Render Markers on Map
    allEvents.forEach(row => {
      const lat = Number(row.latitude);
      const lng = Number(row.longitude);
      if (Number.isFinite(lat) && Number.isFinite(lng)) {
        const marker = L.circleMarker([lat, lng], {
          radius: 3.5,
          color: "#ffffff",
          weight: 0.8,
          fillColor: "#f43f5e",
          fillOpacity: 0.8
        });
        marker.bindPopup(`
          <div style="font-size:12px;">
            <strong style="color:#f43f5e;">GSI Landslide Event</strong><br>
            <strong>Location:</strong> ${escapeHtml(row.location_description)}<br>
            <strong>Historical Date:</strong> ${escapeHtml(row.history_raw)}<br>
            <strong>Material:</strong> ${escapeHtml(row.material_involved)}<br>
            <strong>Movement:</strong> ${escapeHtml(row.movement_type)}<br>
            <small style="color:#94a3b8;">Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}</small>
          </div>
        `);
        marker.addTo(eventLayer);
      }
    });
  }

  /**
   * Load SRTM Terrain Evidence Baseline
   */
  async function loadTerrain() {
    const data = await api("/api/terrain");
    const container = $("terrain-cards");
    if (container && data.records) {
      container.innerHTML = data.records.map(row => `
        <article class="terrain-card">
          <span class="badge-tag tag-amber">DEMO COORD</span>
          <h3>${escapeHtml(row.settlement_name)}</h3>
          <div class="terrain-values">
            <div>
              <strong>${fmt(row.elevation_m, 0)} m</strong>
              <span>Elevation</span>
            </div>
            <div>
              <strong>${fmt(row.slope_deg, 1)}°</strong>
              <span>Mean Slope</span>
            </div>
          </div>
        </article>
      `).join("");
    }
  }

  /**
   * Load IMD Rainfall Series & Summary
   */
  async function loadRain() {
    const yearSelect = $("rain-year");
    const placeSelect = $("rain-place");
    if (!yearSelect) return;

    const year = yearSelect.value || "2024";
    const data = await api(`/api/rainfall?year=${year}`);
    const records = data.records || [];

    const settlementIds = [...new Set(records.map(r => r.settlement_id))];
    if (placeSelect && (!placeSelect.options.length || placeSelect.dataset.year !== year)) {
      placeSelect.dataset.year = year;
      placeSelect.innerHTML = settlementIds.map(id => {
        const match = records.find(r => r.settlement_id === id);
        return `<option value="${escapeHtml(id)}">${escapeHtml(match ? match.settlement_name : id)}</option>`;
      }).join("");
    }

    const currentPlace = placeSelect ? placeSelect.value : settlementIds[0];
    const filtered = records
      .filter(r => r.settlement_id === currentPlace)
      .sort((a, b) => b.date.localeCompare(a.date));

    const tableEl = $("rain-table");
    if (tableEl) {
      tableEl.innerHTML = filtered.slice(0, 14).map(row => `
        <tr>
          <td class="mono">${escapeHtml(row.date)}</td>
          <td class="mono">${fmt(row.rainfall_1d_mm, 1)}</td>
          <td class="mono">${fmt(row.rainfall_3d_mm, 1)}</td>
          <td class="mono">${fmt(row.rainfall_7d_mm, 1)}</td>
        </tr>
      `).join("");
    }

    const readingEl = $("rain-reading");
    if (readingEl) {
      readingEl.textContent = `${records.length} validated daily observation rows for ${year}. No imputation.`;
    }

    const statusEl = $("rain-status");
    if (statusEl) {
      statusEl.textContent = `Showing latest 14 observation dates for selected coordinates (${year}).`;
    }
  }

  /**
   * Load DDMP Documentary Evidence
   */
  async function loadDdmp() {
    const data = await api("/api/ddmp");
    const counts = data.manifest?.explicit_record_counts || {};

    const cardsEl = $("ddmp-cards");
    if (cardsEl) {
      cardsEl.innerHTML = `
        <article>
          <span class="badge-tag tag-cyan">DDMP RECORD</span>
          <h3>${counts.proposed_automatic_rainguage_stations ?? 13} Proposed ARGs</h3>
          <p>DDMP Table 2.6 raingauge network listing</p>
        </article>
        <article>
          <span class="badge-tag tag-cyan">DDMP RECORD</span>
          <h3>${counts.automatic_weather_stations ?? 3} AWS Stations</h3>
          <p>Documented automatic weather stations</p>
        </article>
        <article>
          <span class="badge-tag tag-cyan">DDMP RECORD</span>
          <h3>${counts.gsi_august_2019_landslide_records ?? 24} GSI Aug-2019 Cases</h3>
          <p>Specific post-disaster audit report cases</p>
        </article>
      `;
    }

    const tableEl = $("ddmp-table");
    if (tableEl && data.vulnerability_summary) {
      tableEl.innerHTML = data.vulnerability_summary.map(row => `
        <tr>
          <td><strong>${escapeHtml(row.taluk)}</strong></td>
          <td class="mono">${escapeHtml(row["Very Highly Vulnerable"])}</td>
          <td class="mono">${escapeHtml(row["Highly Vulnerable"])}</td>
          <td class="mono">${escapeHtml(row["Medium Vulnerable"])}</td>
          <td class="mono">${escapeHtml(row["Low Vulnerable"])}</td>
          <td class="mono"><strong>${escapeHtml(row.Total)}</strong></td>
        </tr>
      `).join("");
    }
  }

  /**
   * Render Selected Village Details in Drawer
   */
  function renderVillageDetail(record) {
    if (!record) return;
    selectedVillageLgd = String(record.village_lgd_code);

    const score = Number(record.scenario_susceptibility_0_100 ?? record.ml_susceptibility_0_100 ?? 0);
    const tier = getTierInfo(score);
    const delta = formatDelta(record.susceptibility_delta);

    // Update Header
    const puLabel = $("detail-pu-label");
    if (puLabel) {
      if (record.pu_status === "POSITIVE") {
        puLabel.textContent = "HISTORICAL POSITIVE (GSI EVENT EVIDENCE)";
        puLabel.className = "badge-label";
      } else {
        puLabel.textContent = "UNLABELED LOCATION (NO VERIFIED HISTORICAL EVENTS)";
        puLabel.className = "badge-label text-muted";
      }
    }

    const nameEl = $("detail-village-name");
    if (nameEl) nameEl.textContent = record.village_name_en || "Unknown Village";

    const talukEl = $("detail-village-taluk");
    if (talukEl) talukEl.textContent = `Taluk: ${record.taluk_name_en || "—"}`;

    const lgdEl = $("detail-village-lgd");
    if (lgdEl) lgdEl.textContent = `LGD: ${record.village_lgd_code}`;

    const badgeEl = $("detail-tier-badge");
    if (badgeEl) {
      badgeEl.className = `tier-chip ${tier.className}`;
      badgeEl.textContent = tier.tier;
    }

    const deltaEl = $("detail-delta-badge");
    if (deltaEl) {
      deltaEl.className = `delta-chip ${delta.className}`;
      deltaEl.textContent = delta.text;
    }

    // Hero Score & Bar
    const indexEl = $("detail-index");
    if (indexEl) indexEl.textContent = fmt(score, 1);

    const barEl = $("detail-score-bar");
    if (barEl) barEl.style.width = `${Math.min(100, Math.max(0, score))}%`;

    // 4 Component Breakdown
    const compTerrain = $("comp-terrain");
    if (compTerrain) compTerrain.textContent = `${fmt(record.slope_mean_deg, 1)}°`;
    const compTerrainRaw = $("comp-terrain-raw");
    if (compTerrainRaw) compTerrainRaw.textContent = `Elev: ${fmt(record.elevation_mean_m, 0)}m`;

    const compRain = $("comp-rain");
    const rain7d = record.scenario_rainfall_7d_p95_mm ?? record.rainfall_7d_p95_mm;
    if (compRain) compRain.textContent = `${fmt(rain7d, 1)} mm`;
    const compRainRaw = $("comp-rain-raw");
    const baseRain7d = record.baseline_rainfall_7d_p95_mm ?? record.historical_rainfall_7d_p95_mm;
    if (compRainRaw) compRainRaw.textContent = `Base P95: ${fmt(baseRain7d, 1)}mm`;

    const compEvents = $("comp-events");
    if (compEvents) {
      compEvents.textContent = record.pu_status === "POSITIVE" ? "Verified Case" : "Unlabeled";
    }
    const compEventsRaw = $("comp-events-raw");
    if (compEventsRaw) {
      compEventsRaw.textContent = record.pu_status === "POSITIVE" ? "GSI Containment Match" : "Zero Historical Points";
    }

    const compRain1d = $("comp-rain-1d");
    if (compRain1d) {
      const factor = activeScenarioMeta?.rainfall_factor ?? 1.0;
      const base1d = Number(record.rainfall_1d_max_mm || 180.0);
      compRain1d.textContent = `${fmt(base1d * factor, 1)} mm`;
    }
    const compRain1dRaw = $("comp-rain-1d-raw");
    if (compRain1dRaw) compRain1dRaw.textContent = "Simulated 1D Intensity";

    // Provenance
    const provRainMode = $("prov-rainfall-mode");
    if (provRainMode && activeScenarioMeta) {
      provRainMode.textContent = `In-Memory Scaling (${activeScenarioMeta.scenario_name} · ${activeScenarioMeta.rainfall_factor}x)`;
    }

    const readingEl = $("experimental-reading");
    if (readingEl) {
      readingEl.textContent = `Susceptibility score: ${fmt(score, 1)}/100 (${tier.tier} Tier). Baseline score: ${fmt(record.baseline_susceptibility_0_100, 1)}.`;
    }

    // Highlight active list item
    document.querySelectorAll(".village-rank-item").forEach(item => {
      if (item.dataset.lgd === String(record.village_lgd_code)) {
        item.classList.add("active");
        item.scrollIntoView({ block: "nearest", behavior: "smooth" });
      } else {
        item.classList.remove("active");
      }
    });

    // Zoom / pan map if polygon exists
    const polygon = villagePolygonsMap.get(String(record.village_lgd_code));
    if (polygon && map) {
      map.fitBounds(polygon.getBounds(), { maxZoom: 13, padding: [40, 40] });
      polygon.openPopup();
    }
  }

  /**
   * Render Filtered & Searched Village Ranking List
   */
  function renderRankingList() {
    const listEl = $("index-ranking");
    if (!listEl) return;

    let filtered = [...scenarioRecords];

    // Filter by tier
    if (currentTierFilter !== "all") {
      filtered = filtered.filter(row => {
        const score = Number(row.scenario_susceptibility_0_100 ?? row.ml_susceptibility_0_100);
        const t = getTierInfo(score).tier.toLowerCase();
        return t === currentTierFilter;
      });
    }

    // Filter by search
    if (currentSearchTerm.trim()) {
      const q = currentSearchTerm.toLowerCase();
      filtered = filtered.filter(row => 
        (row.village_name_en && row.village_name_en.toLowerCase().includes(q)) ||
        (row.taluk_name_en && row.taluk_name_en.toLowerCase().includes(q)) ||
        (row.village_lgd_code && String(row.village_lgd_code).includes(q))
      );
    }

    if (!filtered.length) {
      listEl.innerHTML = `<div style="padding:20px;text-align:center;color:#64748b;font-size:12px;">No matching validated villages found.</div>`;
      return;
    }

    listEl.innerHTML = filtered.map((row) => {
      const score = Number(row.scenario_susceptibility_0_100 ?? row.ml_susceptibility_0_100);
      const tier = getTierInfo(score);
      const delta = formatDelta(row.susceptibility_delta);
      const isActive = String(row.village_lgd_code) === String(selectedVillageLgd) ? "active" : "";
      
      // Rank in full scenario dataset
      const rank = scenarioRecords.findIndex(r => String(r.village_lgd_code) === String(row.village_lgd_code)) + 1;

      return `
        <div class="village-rank-item ${isActive}" data-lgd="${escapeHtml(row.village_lgd_code)}" role="option">
          <span class="item-rank">#${rank}</span>
          <div class="item-main">
            <span class="item-name">${escapeHtml(row.village_name_en)}</span>
            <span class="item-taluk">${escapeHtml(row.taluk_name_en)} · ${escapeHtml(row.village_lgd_code)}</span>
          </div>
          <span class="item-score">${fmt(score, 1)}</span>
          <span class="item-delta ${delta.className}">${delta.text}</span>
          <span class="tier-chip ${tier.className}">${tier.label}</span>
        </div>
      `;
    }).join("");

    // Attach click listeners
    listEl.querySelectorAll(".village-rank-item").forEach(item => {
      item.onclick = () => {
        const lgd = item.dataset.lgd;
        const match = scenarioRecords.find(r => String(r.village_lgd_code) === lgd);
        if (match) renderVillageDetail(match);
      };
    });
  }

  /**
   * Update Leaflet Map Polygons styling and popups based on scenario results
   */
  function updateMapPolygons() {
    scenarioRecords.forEach(village => {
      const lgdStr = String(village.village_lgd_code);
      const polygon = villagePolygonsMap.get(lgdStr);
      if (polygon) {
        const score = Number(village.scenario_susceptibility_0_100 ?? village.ml_susceptibility_0_100);
        const tier = getTierInfo(score);
        const delta = formatDelta(village.susceptibility_delta);

        polygon.setStyle({
          color: tier.stroke,
          weight: 1.4,
          fillColor: tier.color,
          fillOpacity: tier.fillOpacity
        });

        polygon.unbindPopup();
        polygon.bindPopup(`
          <div style="font-size:12px;">
            <strong style="color:#38bdf8;">${escapeHtml(village.village_name_en)}</strong><br>
            <strong>Taluk:</strong> ${escapeHtml(village.taluk_name_en)}<br>
            <strong>LGD Code:</strong> ${escapeHtml(village.village_lgd_code)}<br>
            <strong>PU Status:</strong> ${escapeHtml(village.pu_status)}<br>
            <strong>Susceptibility Score:</strong> <strong>${fmt(score, 1)} / 100</strong> (${tier.tier})<br>
            <strong>Scenario Delta:</strong> <span class="${delta.className}">${delta.text}</span><br>
            <strong>Mean Slope:</strong> ${fmt(village.slope_mean_deg, 1)}°<br>
            <small style="color:#94a3b8;">Click to inspect deep village intelligence</small>
          </div>
        `);
      }
    });
  }

  /**
   * Apply Rainfall Scenario via API
   */
  async function applyScenario(scenarioKey = "baseline", customMultiplier = null) {
    try {
      let url = `/api/rainfall-scenario?scenario=${encodeURIComponent(scenarioKey)}`;
      if (customMultiplier !== null) {
        url = `/api/rainfall-scenario?multiplier=${encodeURIComponent(customMultiplier)}`;
      }

      const data = await api(url);
      activeScenarioMeta = data;

      // Sort descending by scenario score
      scenarioRecords = (data.records || []).sort(
        (a, b) => Number(b.scenario_susceptibility_0_100) - Number(a.scenario_susceptibility_0_100)
      );

      // Update Scenario UI Controls
      const badgeEl = $("scenario-status-badge");
      if (badgeEl) {
        badgeEl.textContent = `ACTIVE: ${data.scenario_name.toUpperCase()} (${fmt(data.rainfall_factor, 2)}x)`;
      }

      const outputEl = $("scenario-value");
      if (outputEl) {
        outputEl.textContent = `${fmt(data.rainfall_factor, 2)}x Multiplier (${data.scenario_name})`;
      }

      const sliderEl = $("scenario-slider");
      if (sliderEl && customMultiplier === null) {
        sliderEl.value = data.rainfall_factor;
      }

      // Update Preset Buttons active state
      document.querySelectorAll(".preset-btn").forEach(btn => {
        if (customMultiplier === null && btn.dataset.scenario === scenarioKey) {
          btn.classList.add("active");
        } else {
          btn.classList.remove("active");
        }
      });

      // Update KPI Cards
      const kpiHigh = $("kpi-high-tier");
      if (kpiHigh) kpiHigh.textContent = data.high_tier_count;
      const kpiMed = $("kpi-med-tier");
      if (kpiMed) kpiMed.textContent = data.medium_tier_count;
      const kpiLow = $("kpi-low-tier");
      if (kpiLow) kpiLow.textContent = data.low_tier_count;

      const kpiVillages = $("kpi-villages");
      if (kpiVillages) kpiVillages.textContent = data.record_count;

      // Refresh Map and Ranking List
      updateMapPolygons();
      renderRankingList();

      // Refresh Selected Village Detail
      if (selectedVillageLgd) {
        const match = scenarioRecords.find(r => String(r.village_lgd_code) === selectedVillageLgd);
        if (match) renderVillageDetail(match);
      } else if (scenarioRecords.length > 0) {
        renderVillageDetail(scenarioRecords[0]);
      }
    } catch (err) {
      console.error("Failed to apply rainfall scenario:", err);
    }
  }

  /**
   * Parse and Render Survey of India KMZ Administrative Boundaries
   */
  async function loadBoundaries() {
    const statusEl = $("map-status");
    try {
      const res = await fetch("/data/raw/admin/vb_soi_tn.kmz");
      if (!res.ok) throw new Error(`KMZ fetch HTTP ${res.status}`);

      const zip = await JSZip.loadAsync(await res.arrayBuffer());
      const kmlFile = Object.values(zip.files).find(f => /\.kml$/i.test(f.name));
      if (!kmlFile) throw new Error("No KML found in KMZ archive");

      const xmlText = await kmlFile.async("text");
      const xmlDoc = new DOMParser().parseFromString(xmlText, "application/xml");
      const placemarks = [...xmlDoc.querySelectorAll("Placemark")].filter(p => /nilgiri/i.test(p.textContent));

      let polyCount = 0;
      placemarks.forEach(placemark => {
        const text = placemark.textContent || "";
        let matchedVillage = null;
        for (const v of scenarioRecords) {
          if (v.village_name_en && text.toLowerCase().includes(v.village_name_en.toLowerCase())) {
            matchedVillage = v;
            break;
          }
        }

        placemark.querySelectorAll("Polygon outerBoundaryIs LinearRing coordinates").forEach(coordNode => {
          const rawCoords = coordNode.textContent.trim().split(/\s+/);
          const latLngs = rawCoords
            .map(c => c.split(",").map(Number))
            .filter(c => Number.isFinite(c[0]) && Number.isFinite(c[1]))
            .map(c => [c[1], c[0]]);

          if (latLngs.length > 2) {
            polyCount++;
            let fillColor = "#0284c7";
            let fillOpacity = 0.08;
            let strokeColor = "#38bdf8";

            if (matchedVillage) {
              const score = Number(matchedVillage.scenario_susceptibility_0_100 ?? matchedVillage.ml_susceptibility_0_100);
              const tier = getTierInfo(score);
              fillColor = tier.color;
              strokeColor = tier.stroke;
              fillOpacity = tier.fillOpacity;
            }

            const polygon = L.polygon(latLngs, {
              color: strokeColor,
              weight: 1.2,
              fillColor: fillColor,
              fillOpacity: fillOpacity
            });

            if (matchedVillage) {
              villagePolygonsMap.set(String(matchedVillage.village_lgd_code), polygon);
              const score = fmt(matchedVillage.scenario_susceptibility_0_100 ?? matchedVillage.ml_susceptibility_0_100, 1);
              polygon.bindPopup(`
                <div style="font-size:12px;">
                  <strong style="color:#38bdf8;">${escapeHtml(matchedVillage.village_name_en)}</strong><br>
                  <strong>LGD Code:</strong> ${escapeHtml(matchedVillage.village_lgd_code)}<br>
                  <strong>Susceptibility Score:</strong> ${score} / 100<br>
                  <strong>Mean Slope:</strong> ${fmt(matchedVillage.slope_mean_deg, 1)}°<br>
                  <small style="color:#94a3b8;">Click in Village List for deep breakdown</small>
                </div>
              `);
              polygon.on("click", () => renderVillageDetail(matchedVillage));
            }

            polygon.addTo(boundaryLayer);
          }
        });
      });

      if (statusEl) {
        statusEl.textContent = `${allEvents.length} GSI event markers and ${polyCount} Nilgiris KMZ boundary polygons active.`;
      }
    } catch (err) {
      console.warn("KMZ boundary loading:", err);
      if (statusEl) {
        statusEl.textContent = `${allEvents.length} GSI event markers loaded (KMZ geometry: ${err.message}).`;
      }
    }
  }

  /**
   * Setup Evidence Tab Navigation
   */
  function setupTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    tabs.forEach(btn => {
      btn.onclick = () => {
        tabs.forEach(t => t.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        const targetId = btn.dataset.target;
        const targetPane = $(targetId);
        if (targetPane) targetPane.classList.add("active");
      };
    });
  }

  /**
   * Setup Interactive Scenario Controls
   */
  function setupScenarioControls() {
    // Preset Buttons
    document.querySelectorAll(".preset-btn").forEach(btn => {
      btn.onclick = () => {
        const scenario = btn.dataset.scenario;
        applyScenario(scenario);
      };
    });

    // Multiplier Slider
    const slider = $("scenario-slider");
    const output = $("scenario-value");
    if (slider) {
      slider.oninput = () => {
        const val = Number(slider.value).toFixed(2);
        if (output) output.textContent = `${val}x Multiplier (Custom Simulation)`;
        
        clearTimeout(sliderDebounceTimer);
        sliderDebounceTimer = setTimeout(() => {
          applyScenario("custom", Number(slider.value));
        }, 150);
      };
    }

    // Reset Scenario Button
    const btnResetScenario = $("btn-reset-scenario");
    if (btnResetScenario) {
      btnResetScenario.onclick = () => {
        applyScenario("baseline");
      };
    }

    // Search and Filter Handlers
    const searchInput = $("village-search");
    if (searchInput) {
      searchInput.oninput = e => {
        currentSearchTerm = e.target.value;
        renderRankingList();
      };
    }

    document.querySelectorAll(".filter-pill").forEach(pill => {
      pill.onclick = () => {
        document.querySelectorAll(".filter-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        currentTierFilter = pill.dataset.tier;
        renderRankingList();
      };
    });
  }

  /**
   * Main Initialization Routine
   */
  async function start() {
    try {
      initMap();
      setupTabs();
      setupScenarioControls();

      // Parallel Fetching of Evidence and Scenario Baseline
      await Promise.all([
        loadStatus(),
        loadVillages(),
        loadEvents(),
        loadTerrain(),
        loadDdmp(),
        applyScenario("baseline")
      ]);

      // Rainfall Series & KMZ Boundaries
      await loadRain();
      const rainYear = $("rain-year");
      if (rainYear) rainYear.onchange = () => loadRain();
      const rainPlace = $("rain-place");
      if (rainPlace) rainPlace.onchange = () => loadRain();

      await loadBoundaries();
    } catch (err) {
      console.error("Dashboard initialization error:", err);
      const reasonEl = $("model-reason");
      if (reasonEl) reasonEl.textContent = `Evidence dashboard load failed: ${err.message}`;
    }
  }

  // Launch when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
