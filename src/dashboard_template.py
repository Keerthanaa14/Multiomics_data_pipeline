from pathlib import Path


def create_dashboard_html():

    html = """<!DOCTYPE html>
<html>
<head>
  <title>Multi-Omics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

<h1>Pipeline Dashboard</h1>

<ul id="summary"></ul>

<canvas id="pcaBefore"></canvas>
<canvas id="pcaAfter"></canvas>

<script>

function groupByCategory(data, key) {
  const groups = {};
  data.forEach(d => {
    const val = d[key] || "unknown";
    if (!groups[val]) groups[val] = [];
    groups[val].push({ x: d.PC1, y: d.PC2 });
  });
  return groups;
}

function plotPCA(canvasId, data, colorBy) {
  const grouped = groupByCategory(data, colorBy);

  const datasets = Object.keys(grouped).map(label => ({
    label: label,
    data: grouped[label]
  }));

  new Chart(document.getElementById(canvasId), {
    type: 'scatter',
    data: { datasets: datasets }
  });
}

fetch("dashboard_data.json")
.then(res => res.json())
.then(data => {

  Object.entries(data.summary).forEach(([k,v]) => {
    const li = document.createElement("li");
    li.textContent = k + ": " + v;
    document.getElementById("summary").appendChild(li);
  });

  plotPCA("pcaBefore", data.pca_before, "condition");
  plotPCA("pcaAfter", data.pca_after, "batch");

});

</script>

</body>
</html>
"""

    output_dir = Path("dashboard")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "dashboard.html", "w") as f:
        f.write(html)

    print("Dashboard HTML created")