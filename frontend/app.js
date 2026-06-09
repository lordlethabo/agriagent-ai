const API_URL =
  "https://fluffy-doodle-x54vgjjjj5wr3pg66-8000.app.github.dev/multi-agent-analysis";

const menuBtn = document.getElementById("menuBtn");
const mobileMenu = document.getElementById("mobileMenu");

menuBtn.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
});

function extractScore(text, label) {
  const regex = new RegExp(label + ":\\s*(\\d+)", "i");
  const match = text.match(regex);
  return match ? match[1] : "--";
}

function createScoreCard(title, score) {
  return `
    <div class="score-card">
      <p>${title}</p>
      <strong>${score}/100</strong>
    </div>
  `;
}

function createAgentCard(title, content) {
  return `
    <div class="agent-card">
      <h3>${title}</h3>
      <pre>${content || "No result returned."}</pre>
    </div>
  `;
}

async function analyzeFarm() {
  const status = document.getElementById("status");
  const results = document.getElementById("results");
  const scoreGrid = document.getElementById("scoreGrid");

  status.textContent = "Analyzing...";
  status.className =
    "rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700";

  results.innerHTML = `
    <div class="agent-card">
      <h3>Agents are analyzing the farm</h3>
      <pre>Planner Agent, Water Agent, Risk Agent, and Global Impact Agent are processing the farm profile.</pre>
    </div>
  `;

  scoreGrid.innerHTML = "";

  const payload = {
    location: document.getElementById("location").value,
    farming_goal: document.getElementById("goal").value,
    farm_size: document.getElementById("size").value,
    challenge: document.getElementById("challenge").value
  };

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error("API error: " + response.status);
    }

    const data = await response.json();
    const agents = data.agent_results;
    const impact = agents.global_impact_agent || "";

    scoreGrid.innerHTML =
      createScoreCard("Food Security", extractScore(impact, "Food Security Score")) +
      createScoreCard("Climate Resilience", extractScore(impact, "Climate Resilience Score")) +
      createScoreCard("Water Sustainability", extractScore(impact, "Water Sustainability Score")) +
      createScoreCard("Economic Impact", extractScore(impact, "Economic Impact Score"));

    results.innerHTML =
      createAgentCard("Planner Agent", agents.planner_agent) +
      createAgentCard("Water Agent", agents.water_agent) +
      createAgentCard("Risk Agent", agents.risk_agent) +
      createAgentCard("Global Impact Agent", agents.global_impact_agent);

    status.textContent = "Completed";
    status.className =
      "rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700";

  } catch (error) {
    status.textContent = "Error";
    status.className =
      "rounded-full bg-red-100 px-4 py-2 text-sm font-semibold text-red-700";

    results.innerHTML = `
      <div class="agent-card">
        <h3>Error</h3>
        <pre>${error.message}</pre>
      </div>
    `;
  }
}