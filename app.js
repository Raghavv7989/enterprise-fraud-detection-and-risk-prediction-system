const ws = new WebSocket("ws://localhost:9000/ws");

let riskChart;
let probChart;

function initCharts() {
  riskChart = new Chart(document.getElementById("riskChart"), {
    type: "doughnut",
    data: {
      labels: ["High", "Medium", "Low"],
      datasets: [{
        data: [0, 0, 0],
        backgroundColor: ["#dc2626", "#f59e0b", "#16a34a"]
      }]
    },
    options: { animation: { duration: 600 } }
  });

  probChart = new Chart(document.getElementById("probChart"), {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Fraud Probability (%)",
        data: [],
        backgroundColor: "#2563eb"
      }]
    },
    options: {
      animation: { duration: 600 },
      scales: { y: { beginAtZero: true, max: 100 } }
    }
  });
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  const { transactions, stats, total } = data;

  // KPIs (UNCHANGED UI)
  document.getElementById("total").innerText = total;
  document.getElementById("high").innerText = stats.High;
  document.getElementById("medium").innerText = stats.Medium;
  document.getElementById("low").innerText = stats.Low;

  // Table
  const tbody = document.getElementById("tableBody");
  tbody.innerHTML = "";
  transactions.forEach(tx => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${tx.id}</td>
      <td>${tx.fraud_probability}%</td>
      <td>${tx.risk_score}</td>
      <td>${tx.risk}</td>
    `;
    tbody.appendChild(tr);
  });

  // Charts (UPDATED IN-PLACE)
  riskChart.data.datasets[0].data = [
    stats.High,
    stats.Medium,
    stats.Low
  ];
  riskChart.update();

  probChart.data.labels = transactions.map(t => t.id);
  probChart.data.datasets[0].data =
    transactions.map(t => t.fraud_probability);
  probChart.update();

  // Alert (non-blocking)
  if (data.alert) {
    console.warn("⚠️ High-risk transaction detected");
  }
};

// init once
initCharts();