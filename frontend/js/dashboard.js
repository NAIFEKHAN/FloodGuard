/**
 * FloodGuard Nilgiris Disaster Intelligence — Geospatial Application
 * Phase 4: UI Quality & Professional Polish
 * Strict Scientific Governance: Positive-Unlabeled (PU) Spatial XGBoost, LOTO CV.
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

  // Toast / Status Notification System
  let toastTimer = null;
  const showToast = (message, isError = false, retryFn = null, autoHideMs = 0) => {
    const toast = $("global-toast");
    const toastMsg = $("toast-message");
    const spinner = $("toast-spinner");
    const retryBtn = $("toast-retry-btn");
    if (!toast || !toastMsg) return;

    if (toastTimer) clearTimeout(toastTimer);

    toastMsg.textContent = message;
    toast.style.display = "flex";

    if (spinner) {
      spinner.style.display = isError ? "none" : "block";
    }

    if (isError && retryFn && retryBtn) {
      retryBtn.style.display = "inline-block";
      retryBtn.onclick = () => {
        hideToast();
        retryFn();
      };
    } else if (retryBtn) {
      retryBtn.style.display = "none";
    }

    if (autoHideMs > 0) {
      toastTimer = setTimeout(hideToast, autoHideMs);
    }
  };

  const hideToast = () => {
    const toast = $("global-toast");
    if (toast) toast.style.display = "none";
  };

  const api = async path => {
    try {
      const res = await fetch(path);
      if (!res.ok) throw new Error(`HTTP ${res.status} (${res.statusText})`);
      return await res.json();
    } catch (err) {
      console.error(`API fetch failed for ${path}:`, err);
      throw err;
    }
  };

  // Application State
  let map;
  let susceptibilityLayer;
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
  let activeHighlightedPolygon = null;

  /**
   * Determine Tier classification for demonstration display
   * High: >= 60.0 | Medium: 30.0 - 59.9 | Low: < 30.0
   */
  function getTierInfo(score) {
    const num = Number(score);
    if (num >= 60.0) {
      return { tier: "HIGH", className: "tier-high", label: "HIGH", color: "#ef4444", stroke: "#b91c1c", fillOpacity: 0.30 };
    } else if (num >= 30.0) {
      return { tier: "MEDIUM", className: "tier-medium", label: "MED", color: "#f59e0b", stroke: "#b45309", fillOpacity: 0.24 };
    } else {
      return { tier: "LOW", className: "tier-low", label: "LOW", color: "#10b981", stroke: "#047857", fillOpacity: 0.20 };
    }
  }

  /**
   * Format delta chip
   */
  function formatDelta(delta) {
    const num = Number(delta || 0);
    if (Math.abs(num) < 0.05) {
      return { text: "Δ 0.0 pts", rawText: "0.0 pts", className: "delta-zero", isZero: true };
    } else if (num > 0) {
      return { text: `Δ +${num.toFixed(1)} pts`, rawText: `+${num.toFixed(1)} pts`, className: "delta-pos", isZero: false };
    } else {
      return { text: `Δ ${num.toFixed(1)} pts`, rawText: `${num.toFixed(1)} pts`, className: "delta-neg", isZero: false };
    }
  }

  /**
   * Initialize Leaflet Situation Map
   */
  function initMap() {
    map = L.map("map", {
      center: [11.41, 76.69],
      zoom: 10,
      zoomControl: false,
      attributionControl: true
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "© <a href='https://www.openstreetmap.org/copyright' target='_blank'>OpenStreetMap</a> contributors"
    }).addTo(map);

    susceptibilityLayer = L.layerGroup().addTo(map);
    eventLayer = L.layerGroup().addTo(map);
    boundaryLayer = L.layerGroup().addTo(map);
    centroidLayer = L.layerGroup().addTo(map);

    // Custom Map Action Controls
    const btnZoomIn = $("btn-zoom-in");
    if (btnZoomIn) btnZoomIn.onclick = () => map.zoomIn();

    const btnZoomOut = $("btn-zoom-out");
    if (btnZoomOut) btnZoomOut.onclick = () => map.zoomOut();

    const btnReset = $("btn-reset-map");
    if (btnReset) {
      btnReset.onclick = () => {
        map.flyTo([11.41, 76.69], 10, { duration: 0.8 });
        showToast("Map view centered on Nilgiris District", false, null, 1500);
      };
    }

    const btnFullscreen = $("btn-fullscreen");
    if (btnFullscreen) {
      btnFullscreen.onclick = () => {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen().catch(() => {});
        } else {
          document.exitFullscreen().catch(() => {});
        }
      };
    }

    // Layers Popup Toggle
    const btnToggleLayers = $("btn-toggle-layers");
    const layersPopup = $("layers-popup");
    if (btnToggleLayers && layersPopup) {
      btnToggleLayers.onclick = e => {
        e.stopPropagation();
        const isOpen = layersPopup.style.display === "block";
        layersPopup.style.display = isOpen ? "none" : "block";
        btnToggleLayers.setAttribute("aria-expanded", String(!isOpen));
      };
      document.addEventListener("click", e => {
        if (layersPopup && !layersPopup.contains(e.target) && e.target !== btnToggleLayers) {
          layersPopup.style.display = "none";
          btnToggleLayers.setAttribute("aria-expanded", "false");
        }
      });
    }

    // Layer Checkbox Toggles
    const toggleSusc = $("toggle-susceptibility");
    if (toggleSusc) {
      toggleSusc.onchange = e => {
        if (e.target.checked) {
          map.addLayer(susceptibilityLayer);
          showToast("Susceptibility Zones enabled", false, null, 1200);
        } else {
          map.removeLayer(susceptibilityLayer);
          showToast("Susceptibility Zones hidden", false, null, 1200);
        }
      };
    }

    const toggleEvents = $("toggle-events");
    if (toggleEvents) {
      toggleEvents.onchange = e => {
        if (e.target.checked) {
          map.addLayer(eventLayer);
          showToast("GSI Landslides layer enabled", false, null, 1200);
        } else {
          map.removeLayer(eventLayer);
          showToast("GSI Landslides layer hidden", false, null, 1200);
        }
      };
    }

    const toggleBoundaries = $("toggle-boundaries");
    if (toggleBoundaries) {
      toggleBoundaries.onchange = e => {
        if (e.target.checked) {
          map.addLayer(boundaryLayer);
          showToast("Administrative boundaries enabled", false, null, 1200);
        } else {
          map.removeLayer(boundaryLayer);
          showToast("Administrative boundaries hidden", false, null, 1200);
        }
      };
    }

    const toggleCentroids = $("toggle-centroids");
    if (toggleCentroids) {
      toggleCentroids.onchange = e => {
        if (e.target.checked) {
          map.addLayer(centroidLayer);
          showToast("Village markers enabled", false, null, 1200);
        } else {
          map.removeLayer(centroidLayer);
          showToast("Village markers hidden", false, null, 1200);
        }
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
        reasonEl.textContent = `PU-ML Active · 25 Positive · 15 Unlabeled · 6-Fold LOTO CV (ROC-AUC ${fmt(data.loto_roc_auc, 4)}) · UNLABELED ≠ NO RISK`;
      }
    } catch (err) {
      console.warn("Status fetch warning:", err);
    }
  }

  /**
   * Load Administrative Framework & Reconciliation
   */
  async function loadVillages() {
    try {
      const data = await api("/api/villages?limit=102");
      const summaryEl = $("village-summary");
      if (summaryEl) {
        summaryEl.textContent = `${data.record_count} Village Master records; ${data.exact_spatial_matches} exact LGD matches. ${data.village_master_only} Master-only and ${data.kmz_only} KMZ-only records remain unmatched.`;
      }

      const tableEl = $("village-table");
      if (tableEl) {
        tableEl.innerHTML = (data.records || []).slice(0, 15).map(row => `
          <tr>
            <td>${escapeHtml(row.village_name_en)}</td>
            <td>${escapeHtml(row.taluk_name_en)}</td>
            <td class="mono">${escapeHtml(row.village_lgd_code)}</td>
          </tr>
        `).join("");
      }
    } catch (err) {
      console.warn("Villages fetch warning:", err);
    }
  }

  /**
   * Load GSI / NLFC Landslide Event Inventory
   */
  async function loadEvents() {
    try {
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

      // Render Distinct Historical GSI Markers on Map with reduced visual clutter
      allEvents.forEach(row => {
        const lat = Number(row.latitude);
        const lng = Number(row.longitude);
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
          const marker = L.circleMarker([lat, lng], {
            radius: 3.0,
            color: "#ffffff",
            weight: 1.0,
            fillColor: "#e11d48",
            fillOpacity: 0.75
          });
          marker.bindPopup(`
            <div style="font-size:12px;">
              <strong style="color:#e11d48;font-size:13px;">Historical GSI Landslide Point</strong><br>
              <strong>Location:</strong> ${escapeHtml(row.location_description)}<br>
              <strong>Historical Date:</strong> ${escapeHtml(row.history_raw)}<br>
              <strong>Material:</strong> ${escapeHtml(row.material_involved)}<br>
              <strong>Movement:</strong> ${escapeHtml(row.movement_type)}<br>
              <small style="color:#64748b;">Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}</small><br>
              <small style="color:#94a3b8;font-style:italic;">Historical GSI inventory record; not a live event.</small>
            </div>
          `);
          marker.addTo(eventLayer);
        }
      });
    } catch (err) {
      console.warn("Events fetch warning:", err);
    }
  }

  /**
   * Load SRTM Terrain Evidence Baseline
   */
  async function loadTerrain() {
    try {
      const data = await api("/api/terrain");
      const container = $("terrain-cards");
      if (container && data.records) {
        container.innerHTML = data.records.map(row => `
          <article class="terrain-card">
            <span class="badge-tag tag-cyan">DEMO COORD</span>
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
    } catch (err) {
      console.warn("Terrain fetch warning:", err);
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
    try {
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
    } catch (err) {
      console.warn("Rain fetch warning:", err);
    }
  }

  /**
   * Highlight polygon on map
   */
  function highlightPolygon(polygon, score) {
    if (activeHighlightedPolygon && activeHighlightedPolygon !== polygon) {
      const oldScore = activeHighlightedPolygon._floodguardScore || 0;
      const oldTier = getTierInfo(oldScore);
      activeHighlightedPolygon.setStyle({
        color: oldTier.stroke,
        weight: 1.5,
        fillOpacity: oldTier.fillOpacity
      });
      if (activeHighlightedPolygon._path) {
        L.DomUtil.removeClass(activeHighlightedPolygon._path, "polygon-selected");
      }
    }

    if (polygon) {
      polygon._floodguardScore = score;
      polygon.setStyle({
        color: "#0284c7",
        weight: 3.5,
        fillOpacity: 0.45
      });
      if (polygon._path) {
        L.DomUtil.addClass(polygon._path, "polygon-selected");
      }
      polygon.bringToFront();
      activeHighlightedPolygon = polygon;
    }
  }

  /**
   * Render Selected Village Details in Decision Support Card / Bottom Sheet
   */
  function renderVillageDetail(record) {
    if (!record) return;
    selectedVillageLgd = String(record.village_lgd_code);

    const panel = $("village-detail-panel");
    if (panel) {
      panel.style.display = "flex";
    }

    const score = Number(record.scenario_susceptibility_0_100 ?? record.ml_susceptibility_0_100 ?? 0);
    const baseScore = Number(record.baseline_susceptibility_0_100 ?? record.ml_susceptibility_0_100 ?? score);
    const tier = getTierInfo(score);
    const delta = formatDelta(record.susceptibility_delta);

    // Update Header
    const puLabel = $("detail-pu-label");
    if (puLabel) {
      if (record.pu_status === "POSITIVE") {
        puLabel.textContent = "HISTORICAL POSITIVE (GSI EVENT EVIDENCE)";
        puLabel.className = "badge-label";
      } else {
        puLabel.textContent = "UNLABELED LOCATION (UNLABELED ≠ NO RISK)";
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
      badgeEl.textContent = `${tier.tier} RISK`;
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

    // Scenario Impact Breakdown
    const baseScoreEl = $("detail-base-score");
    if (baseScoreEl) baseScoreEl.textContent = `${fmt(baseScore, 1)}`;

    const scenScoreEl = $("detail-scenario-score");
    if (scenScoreEl) scenScoreEl.textContent = `${fmt(score, 1)}`;

    const deltaValEl = $("detail-delta-val");
    if (deltaValEl) {
      deltaValEl.textContent = delta.rawText;
      deltaValEl.className = `comp-sub-val delta-val ${delta.className}`;
    }

    const deltaNoteEl = $("detail-delta-note");
    if (deltaNoteEl) {
      deltaNoteEl.textContent = delta.isZero ? "Historical baseline expectation" : "vs Historical Baseline";
    }

    // 4 Component Breakdown
    const compTerrain = $("comp-terrain");
    if (compTerrain) compTerrain.textContent = `${fmt(record.slope_mean_deg, 1)}°`;
    const compTerrainRaw = $("comp-terrain-raw");
    const maxSlope = record.slope_max_deg ? ` · Max: ${fmt(record.slope_max_deg, 1)}°` : "";
    if (compTerrainRaw) compTerrainRaw.textContent = `Elev: ${fmt(record.elevation_mean_m, 0)}m${maxSlope}`;

    const compRain = $("comp-rain");
    const rain7d = record.scenario_rainfall_7d_p95_mm ?? record.rainfall_7d_p95_mm;
    if (compRain) compRain.textContent = `${fmt(rain7d, 1)} mm`;
    const compRainRaw = $("comp-rain-raw");
    const baseRain7d = record.baseline_rainfall_7d_p95_mm ?? record.historical_rainfall_7d_p95_mm;
    if (compRainRaw) compRainRaw.textContent = `Base P95: ${fmt(baseRain7d, 1)}mm`;

    const compEvents = $("comp-events");
    if (compEvents) {
      compEvents.textContent = record.pu_status === "POSITIVE" ? "1 Verified Match" : "UNLABELED";
    }
    const compEventsRaw = $("comp-events-raw");
    if (compEventsRaw) {
      compEventsRaw.textContent = record.pu_status === "POSITIVE" 
        ? "GSI Strict Containment" 
        : "No recorded GSI inventory evidence";
    }

    const compRain1d = $("comp-rain-1d");
    if (compRain1d) {
      const factor = activeScenarioMeta?.rainfall_factor ?? 1.0;
      const base1d = Number(record.rainfall_1d_max_mm || 180.0);
      compRain1d.textContent = `${fmt(base1d * factor, 1)} mm`;
    }
    const compRain1dRaw = $("comp-rain-1d-raw");
    if (compRain1dRaw) compRain1dRaw.textContent = "Simulated 1D Peak";

    // GSI Evidence Card description
    const gsiDescEl = $("detail-gsi-desc");
    if (gsiDescEl) {
      gsiDescEl.textContent = record.pu_status === "POSITIVE"
        ? "Historical landslide inventory event matched"
        : "UNLABELED (Absence of recorded inventory evidence)";
    }

    // Provenance
    const provRainMode = $("prov-rainfall-mode");
    if (provRainMode && activeScenarioMeta) {
      provRainMode.textContent = `In-Memory Scaling (${activeScenarioMeta.scenario_name} · ${activeScenarioMeta.rainfall_factor}x)`;
    }

    // Highlight active list item in ranking
    document.querySelectorAll(".village-rank-item").forEach(item => {
      if (item.dataset.lgd === String(record.village_lgd_code)) {
        item.classList.add("active");
        item.scrollIntoView({ block: "nearest", behavior: "smooth" });
      } else {
        item.classList.remove("active");
      }
    });

    // Zoom and highlight polygon on map
    const polygon = villagePolygonsMap.get(String(record.village_lgd_code));
    if (polygon && map) {
      map.fitBounds(polygon.getBounds(), { maxZoom: 13, padding: [50, 50] });
      highlightPolygon(polygon, score);
      polygon.openPopup();
    }
  }

  /**
   * Render Filtered & Searched Village Ranking Dropdown List
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

    // Case-insensitive Search by Name, Partial Name, Taluk, LGD code
    if (currentSearchTerm.trim()) {
      const q = currentSearchTerm.toLowerCase().trim();
      filtered = filtered.filter(row => 
        (row.village_name_en && row.village_name_en.toLowerCase().includes(q)) ||
        (row.taluk_name_en && row.taluk_name_en.toLowerCase().includes(q)) ||
        (row.village_lgd_code && String(row.village_lgd_code).includes(q))
      );
    }

    if (!filtered.length) {
      listEl.innerHTML = `
        <div class="empty-results-box">
          <span class="empty-results-title">No matching villages found</span>
          <span>No results in the 40-village universe for this query/filter.</span>
        </div>
      `;
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
        <div class="village-rank-item ${isActive}" data-lgd="${escapeHtml(row.village_lgd_code)}" role="option" tabindex="0">
          <span class="item-rank">#${rank}</span>
          <div class="item-main">
            <span class="item-name">${escapeHtml(row.village_name_en)}</span>
            <span class="item-taluk">${escapeHtml(row.taluk_name_en)} · LGD ${escapeHtml(row.village_lgd_code)}</span>
          </div>
          <span class="item-score">${fmt(score, 1)}</span>
          <span class="item-delta ${delta.className}" title="Change from historical baseline">${delta.text}</span>
          <span class="tier-chip ${tier.className}">${tier.label}</span>
        </div>
      `;
    }).join("");

    // Attach click listeners
    listEl.querySelectorAll(".village-rank-item").forEach(item => {
      item.onclick = () => {
        const lgd = item.dataset.lgd;
        const match = scenarioRecords.find(r => String(r.village_lgd_code) === lgd);
        if (match) {
          renderVillageDetail(match);
          showToast(`Selected ${match.village_name_en}`, false, null, 1500);
        }
      };
      item.onkeydown = e => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          item.click();
        }
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

        polygon._floodguardScore = score;

        // If not actively highlighted, apply tier stroke
        if (polygon !== activeHighlightedPolygon) {
          polygon.setStyle({
            color: tier.stroke,
            weight: 1.5,
            fillColor: tier.color,
            fillOpacity: tier.fillOpacity
          });
        } else {
          polygon.setStyle({
            fillColor: tier.color
          });
        }

        polygon.unbindTooltip();
        polygon.bindTooltip(`
          <strong>${escapeHtml(village.village_name_en)}</strong> (${fmt(score, 1)} / 100 - ${tier.tier})
        `, { sticky: true, className: "polygon-tooltip" });

        polygon.unbindPopup();
        polygon.bindPopup(`
          <div style="font-size:12px;">
            <strong style="color:#0284c7;font-size:13px;">${escapeHtml(village.village_name_en)}</strong><br>
            <strong>Taluk:</strong> ${escapeHtml(village.taluk_name_en)}<br>
            <strong>LGD Code:</strong> ${escapeHtml(village.village_lgd_code)}<br>
            <strong>PU Status:</strong> ${escapeHtml(village.pu_status)}<br>
            <strong>Susceptibility Score:</strong> <strong>${fmt(score, 1)} / 100</strong> (${tier.tier})<br>
            <strong>Scenario Delta:</strong> <span class="${delta.className}">${delta.text}</span><br>
            <strong>Mean Slope:</strong> ${fmt(village.slope_mean_deg, 1)}°<br>
            <small style="color:#0284c7;font-weight:600;">Click polygon for detailed view</small>
          </div>
        `);
      }
    });
  }

  /**
   * Apply Rainfall Scenario via API & Synchronize all UI Elements
   */
  async function applyScenario(scenarioKey = "baseline", customMultiplier = null) {
    try {
      showToast("Updating scenario simulation…");

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
        badgeEl.textContent = `${fmt(data.rainfall_factor, 2)}x ${data.scenario_name}`;
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

      // Update Risk Overview Card Title/Subtitle and Counts
      const overviewContext = $("overview-scenario-context");
      if (overviewContext) {
        overviewContext.textContent = `${data.scenario_name} · ${fmt(data.rainfall_factor, 2)}×`;
      }

      const overviewHigh = $("overview-count-high");
      if (overviewHigh) overviewHigh.textContent = data.high_tier_count;
      const overviewMed = $("overview-count-med");
      if (overviewMed) overviewMed.textContent = data.medium_tier_count;
      const overviewLow = $("overview-count-low");
      if (overviewLow) overviewLow.textContent = data.low_tier_count;

      // Update Filter Pill Badges
      const kpiHigh = $("kpi-high-tier");
      if (kpiHigh) kpiHigh.textContent = data.high_tier_count;
      const kpiMed = $("kpi-med-tier");
      if (kpiMed) kpiMed.textContent = data.medium_tier_count;
      const kpiLow = $("kpi-low-tier");
      if (kpiLow) kpiLow.textContent = data.low_tier_count;
      const kpiVillages = $("kpi-villages");
      if (kpiVillages) kpiVillages.textContent = data.record_count;

      // Refresh Map and Ranking Dropdown List
      updateMapPolygons();
      renderRankingList();

      // Refresh Selected Village Detail if panel is open
      if (selectedVillageLgd) {
        const match = scenarioRecords.find(r => String(r.village_lgd_code) === selectedVillageLgd);
        if (match) renderVillageDetail(match);
      }

      hideToast();
    } catch (err) {
      console.error("Failed to apply rainfall scenario:", err);
      showToast("Unable to connect to FloodGuard API", true, () => applyScenario(scenarioKey, customMultiplier));
    }
  }

  /**
   * Parse and Render Survey of India KMZ Administrative Boundaries
   */
  async function loadBoundaries() {
    try {
      const res = await fetch("/data/raw/admin/vb_soi_tn.kmz");
      if (!res.ok) throw new Error(`KMZ fetch HTTP ${res.status}`);

      const zip = await JSZip.loadAsync(await res.arrayBuffer());
      const kmlFile = Object.values(zip.files).find(f => /\.kml$/i.test(f.name));
      if (!kmlFile) throw new Error("No KML found in KMZ archive");

      const xmlText = await kmlFile.async("text");
      const xmlDoc = new DOMParser().parseFromString(xmlText, "application/xml");
      const placemarks = [...xmlDoc.querySelectorAll("Placemark")].filter(p => /nilgiri/i.test(p.textContent));

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
            let fillColor = "#0284c7";
            let fillOpacity = 0.18;
            let strokeColor = "#0ea5e9";

            if (matchedVillage) {
              const score = Number(matchedVillage.scenario_susceptibility_0_100 ?? matchedVillage.ml_susceptibility_0_100);
              const tier = getTierInfo(score);
              fillColor = tier.color;
              strokeColor = tier.stroke;
              fillOpacity = tier.fillOpacity;
            }

            const polygon = L.polygon(latLngs, {
              color: strokeColor,
              weight: 1.5,
              fillColor: fillColor,
              fillOpacity: fillOpacity
            });

            if (matchedVillage) {
              polygon._floodguardScore = Number(matchedVillage.scenario_susceptibility_0_100 ?? matchedVillage.ml_susceptibility_0_100);
              villagePolygonsMap.set(String(matchedVillage.village_lgd_code), polygon);
              const score = fmt(matchedVillage.scenario_susceptibility_0_100 ?? matchedVillage.ml_susceptibility_0_100, 1);
              
              polygon.bindTooltip(`
                <strong>${escapeHtml(matchedVillage.village_name_en)}</strong> (${score} / 100)
              `, { sticky: true, className: "polygon-tooltip" });

              polygon.bindPopup(`
                <div style="font-size:12px;">
                  <strong style="color:#0284c7;font-size:13px;">${escapeHtml(matchedVillage.village_name_en)}</strong><br>
                  <strong>LGD Code:</strong> ${escapeHtml(matchedVillage.village_lgd_code)}<br>
                  <strong>Susceptibility Score:</strong> ${score} / 100<br>
                  <strong>Mean Slope:</strong> ${fmt(matchedVillage.slope_mean_deg, 1)}°<br>
                  <small style="color:#0284c7;font-weight:600;">Click for full village details</small>
                </div>
              `);
              polygon.on("click", () => renderVillageDetail(matchedVillage));

              // Add center circle marker for centroid layer
              const center = polygon.getBounds().getCenter();
              const marker = L.circleMarker(center, {
                radius: 4,
                color: "#ffffff",
                weight: 1.5,
                fillColor: "#0284c7",
                fillOpacity: 0.9
              });
              marker.bindTooltip(`<strong>${escapeHtml(matchedVillage.village_name_en)}</strong>`);
              marker.on("click", () => renderVillageDetail(matchedVillage));
              marker.addTo(centroidLayer);
            }

            polygon.addTo(susceptibilityLayer);
          }
        });
      });
    } catch (err) {
      console.warn("KMZ boundary loading warning:", err);
    }
  }

  /**
   * Setup UI Controls & Interactive Listeners
   */
  function setupUIListeners() {
    // Search input
    const searchInput = $("village-search");
    const clearBtn = $("btn-clear-search");
    if (searchInput) {
      searchInput.oninput = e => {
        currentSearchTerm = e.target.value;
        if (clearBtn) clearBtn.style.display = currentSearchTerm ? "flex" : "none";
        renderRankingList();
      };
      searchInput.onkeydown = e => {
        if (e.key === "Escape") {
          searchInput.value = "";
          currentSearchTerm = "";
          if (clearBtn) clearBtn.style.display = "none";
          renderRankingList();
        }
      };
    }
    if (clearBtn) {
      clearBtn.onclick = () => {
        if (searchInput) {
          searchInput.value = "";
          currentSearchTerm = "";
          clearBtn.style.display = "none";
          renderRankingList();
          searchInput.focus();
        }
      };
    }

    // Tier Filter Pills
    document.querySelectorAll(".filter-pill").forEach(pill => {
      pill.onclick = () => {
        document.querySelectorAll(".filter-pill").forEach(p => {
          p.classList.remove("active");
          p.setAttribute("aria-selected", "false");
        });
        pill.classList.add("active");
        pill.setAttribute("aria-selected", "true");
        currentTierFilter = pill.dataset.tier;
        renderRankingList();
      };
    });

    // Close Village Detail Panel Button
    const btnCloseDetail = $("btn-close-detail");
    const detailPanel = $("village-detail-panel");
    if (btnCloseDetail && detailPanel) {
      btnCloseDetail.onclick = () => {
        detailPanel.style.display = "none";
        selectedVillageLgd = null;
        if (activeHighlightedPolygon) {
          const oldScore = activeHighlightedPolygon._floodguardScore || 0;
          const oldTier = getTierInfo(oldScore);
          activeHighlightedPolygon.setStyle({
            color: oldTier.stroke,
            weight: 1.5,
            fillOpacity: oldTier.fillOpacity
          });
          if (activeHighlightedPolygon._path) {
            L.DomUtil.removeClass(activeHighlightedPolygon._path, "polygon-selected");
          }
          activeHighlightedPolygon = null;
        }
        document.querySelectorAll(".village-rank-item").forEach(item => item.classList.remove("active"));
      };
    }

    // Evidence Modal Toggle
    const btnOpenEvidence = $("btn-open-evidence");
    const btnCloseEvidence = $("btn-close-evidence");
    const modalBackdrop = $("modal-backdrop");
    const evidenceModal = $("evidence-modal");

    const openModal = (defaultTabId = null) => {
      if (evidenceModal) {
        evidenceModal.style.display = "flex";
        if (defaultTabId) {
          const tabBtn = document.querySelector(`.modal-tabs .tab-btn[data-target="${defaultTabId}"]`);
          if (tabBtn) tabBtn.click();
        }
      }
    };
    const closeModal = () => { if (evidenceModal) evidenceModal.style.display = "none"; };

    if (btnOpenEvidence) btnOpenEvidence.onclick = () => openModal();
    if (btnCloseEvidence) btnCloseEvidence.onclick = closeModal;
    if (modalBackdrop) modalBackdrop.onclick = closeModal;

    // View Village Evidence Button in Detail Panel
    const btnViewVillageEvidence = $("btn-view-village-evidence");
    if (btnViewVillageEvidence) {
      btnViewVillageEvidence.onclick = () => openModal("tab-events");
    }

    // Evidence Tabs
    const tabs = document.querySelectorAll(".modal-tabs .tab-btn");
    tabs.forEach(btn => {
      btn.onclick = () => {
        tabs.forEach(t => {
          t.classList.remove("active");
          t.setAttribute("aria-selected", "false");
        });
        document.querySelectorAll(".modal-body-scroll .tab-pane").forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
        const targetId = btn.dataset.target;
        const targetPane = $(targetId);
        if (targetPane) targetPane.classList.add("active");
      };
    });

    // Scenario Presets
    document.querySelectorAll(".preset-btn").forEach(btn => {
      btn.onclick = () => {
        const scenario = btn.dataset.scenario;
        applyScenario(scenario);
      };
    });

    // Scenario Multiplier Slider with Debounce
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
        showToast("Precipitation scenario reset to 1.00x baseline", false, null, 1500);
      };
    }
  }

  /**
   * Main Initialization Routine
   */
  async function start() {
    try {
      initMap();
      setupUIListeners();

      // Parallel Fetching of Baseline Evidence and Scenario
      await Promise.all([
        loadStatus(),
        loadVillages(),
        loadEvents(),
        loadTerrain(),
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
      showToast("Unable to connect to FloodGuard API", true, start);
    }
  }

  // Launch when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
