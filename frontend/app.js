const API_URL =
  "https://fluffy-doodle-x54vgjjjj5wr3pg66-8000.app.github.dev/multi-agent-analysis";

const menuBtn = document.getElementById("menuBtn");
const mobileMenu = document.getElementById("mobileMenu");

if (menuBtn) {
  menuBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });
}

function getScore(text, label) {
  const match = text.match(new RegExp(`${label}:\\s*(\\d+)`, "i"));
  return match ? parseInt(match[1]) : 0;
}

function createScoreCard(title, score) {
  return `
    <div class="score-card">
      <p>${title}</p>
      <strong>${score}</strong>

      <div class="progress-track">
        <div
          class="progress-fill"
          style="width:${score}%">
        </div>
      </div>
    </div>
  `;
}

function createAgentCard(title, content) {
  return `
    <div class="agent-card">
      <h3>${title}</h3>
      <pre>${content}</pre>
    </div>
  `;
}

function showLoading() {
  document.getElementById("results").innerHTML = `
    <div class="agent-card">
      <h3>Analyzing Farm Profile</h3>
      <pre>
Planner Agent is evaluating strategy...
Water Agent is evaluating sustainability...
Risk Agent is evaluating threats...
Global Impact Agent is calculating impact...

Please wait...
      </pre>
    </div>
  `;
}

function showError(message) {
  document.getElementById("results").innerHTML = `
    <div class="agent-card">
      <h3>Analysis Failed</h3>
      <pre>${message}</pre>
    </div>
  `;
}

async function analyzeFarm() {
  const status = document.getElementById("status");
  const scoreGrid = document.getElementById("scoreGrid");
  const results = document.getElementById("results");

  status.textContent = "Running Analysis";

  scoreGrid.innerHTML = "";
  showLoading();

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
      throw new Error(
        `API returned status ${response.status}`
      );
    }

    const data = await response.json();

    const planner =
      data.agent_results.planner_agent || "No response.";

    const water =
      data.agent_results.water_agent || "No response.";

    const risk =
      data.agent_results.risk_agent || "No response.";

    const impact =
      data.agent_results.global_impact_agent || "No response.";

    const foodScore =
      getScore(impact, "Food Security Score");

    const climateScore =
      getScore(impact, "Climate Resilience Score");

    const waterScore =
      getScore(impact, "Water Sustainability Score");

    const economicScore =
      getScore(impact, "Economic Impact Score");

    scoreGrid.innerHTML =
      createScoreCard("Food Security", foodScore) +
      createScoreCard("Climate Resilience", climateScore) +
      createScoreCard("Water Sustainability", waterScore) +
      createScoreCard("Economic Impact", economicScore);

    results.innerHTML =
      createAgentCard("Planner Agent", planner) +
      createAgentCard("Water Agent", water) +
      createAgentCard("Risk Agent", risk) +
      createAgentCard("Global Impact Agent", impact);

    status.textContent = "Analysis Complete";
  } catch (error) {
    console.error(error);

    status.textContent = "Error";

    showError(
      "Unable to connect to AgriAgent Global API. Verify that your FastAPI backend is running and accessible."
    );
  }
}
