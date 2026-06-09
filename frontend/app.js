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
      <strong>${score}/100</strong>
      <div class="progress-track">
        <div class="progress-fill" style="width:${score}%"></div>
      </div>
    </div>
  `;
}

function createOverallScore(score) {
  return `
    <div class="overall-score-card">
      <div>
        <p>Overall Sustainability Score</p>
        <h3>${score}/100</h3>
        <span>Combined food security, climate, water, and economic impact rating.</span>
      </div>
      <div class="overall-ring">
        <span>${score}</span>
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
      <h3>Running Multi-Agent Analysis</h3>
      <pre>Planner Agent is evaluating strategy...
Water Agent is evaluating sustainability...
Risk Agent is evaluating threats...
Global Impact Agent is calculating impact scores...

Please wait while AgriAgent Global completes the analysis.</pre>
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
      throw new Error(`API returned status ${response.status}`);
    }

    const data = await response.json();
    const agents = data.agent_results;
    const impact = agents.global_impact_agent || "";

    const foodScore = getScore(impact, "Food Security Score");
    const climateScore = getScore(impact, "Climate Resilience Score");
    const waterScore = getScore(impact, "Water Sustainability Score");
    const economicScore = getScore(impact, "Economic Impact Score");

    const scores = [foodScore, climateScore, waterScore, economicScore].filter(
      score => score > 0
    );

    const overallScore =
      scores.length > 0
        ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length)
        : 0;

    scoreGrid.innerHTML =
      createOverallScore(overallScore) +
      createScoreCard("Food Security", foodScore) +
      createScoreCard("Climate Resilience", climateScore) +
      createScoreCard("Water Sustainability", waterScore) +
      createScoreCard("Economic Impact", economicScore);

    results.innerHTML =
      createAgentCard("Planner Agent", agents.planner_agent || "No response.") +
      createAgentCard("Water Agent", agents.water_agent || "No response.") +
      createAgentCard("Risk Agent", agents.risk_agent || "No response.") +
      createAgentCard("Global Impact Agent", impact || "No response.");

    status.textContent = "Analysis Complete";
  } catch (error) {
    console.error(error);
    status.textContent = "Error";

    showError(
      "Unable to connect to AgriAgent Global API. Verify that your FastAPI backend is running and accessible."
    );
  }
}
