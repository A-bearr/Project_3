let map;
let markersLayer;

document.addEventListener("DOMContentLoaded", function () {
  map = L.map("map").setView([20, 0], 2);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);

  // Dropdown change listener
  document.getElementById("metric-select").addEventListener("change", function () {
    const selectedMetric = this.value;
    loadMetricData(selectedMetric);
  });

  // Load default metric (Revenue)
  loadMetricData("Revenue");
});

function loadMetricData(metric) {
  fetch(`/api/metric/${metric}`)
    .then((response) => {
      if (!response.ok) throw new Error("API request failed");
      return response.json();
    })
    .then((data) => {
      if (markersLayer) {
        map.removeLayer(markersLayer); // Clear old markers
      }

      markersLayer = L.layerGroup();

      data.forEach((company) => {
        let label, popup;

        if (metric === "All") {
          label = "🏆";
          popup = `
            <strong>${company.company}</strong><br>
            Ticker: ${company.ticker}<br>
            Revenue: $${Number(company.values.Revenue).toLocaleString()} (Rank ${company.ranks.Revenue})<br>
            Earnings: $${Number(company.values.Earnings).toLocaleString()} (Rank ${company.ranks.Earnings})<br>
            Market Cap: $${Number(company.values["Market Cap"]).toLocaleString()} (Rank ${company.ranks["Market Cap"]})
          `;
        } else {
          const value = company.value;
          const rank = company.rank;
          label = `${rank} 🏆 ${metric[0].toUpperCase()}`;
          popup = `
            <strong>${company.company}</strong><br>
            Ticker: ${company.ticker}<br>
            ${metric}: $${Number(value).toLocaleString()}
          `;
        }

        const marker = L.marker([company.lat, company.lon])
          .bindPopup(popup)
          .bindTooltip(label, {
            permanent: true,
            direction: "top",
            className: "marker-label"
          });

        markersLayer.addLayer(marker);
      });

      markersLayer.addTo(map);
    })
    .catch((error) => {
      console.error("Error loading data:", error);
    });
}


  