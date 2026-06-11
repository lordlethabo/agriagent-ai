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

function createRecommendationCard(recommendation, confidence, agents) {
  const reasons = agents.map(agent => `<li>${agent.finding}</li>`).join("");

  return `
    <div class="recommendation-card">
      <h3>Recommendation</h3>
      <p><strong>Best action:</strong> ${recommendation}</p>
      <p><strong>Confidence:</strong> ${confidence}%</p>

      <h4>Why this recommendation?</h4>
      <ul>${reasons}</ul>
    </div>
  `;
}

function createTimeline(agents) {
  return `
    <div class="agent-card">
      <h3>Agent Reasoning Timeline</h3>
      <div class="timeline">
        ${agents.map(agent => `
          <div class="timeline-step">
            <strong>${agent.name}</strong>
            <span>${agent.status}</span>
            <p>${agent.finding}</p>
          </div>
        `).join("")}
      </div>
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

function createSafetyNote(note) {
  return `
    <div class="safety-note">
      ${note}
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
Coordinator Agent is preparing the final recommendation.</pre>
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

    const agents = data.agent_results || {};
    const timelineAgents = data.agents || [];
    const impact = agents.global_impact_agent || "";

    const foodScore = getScore(impact, "Food Security Score");
    const climateScore = getScore(impact, "Climate Resilience Score");
    const waterScore = getScore(impact, "Water Sustainability Score");
    const economicScore = getScore(impact, "Economic Impact Score");

    scoreGrid.innerHTML =
      createScoreCard("Food Security", foodScore) +
      createScoreCard("Climate Resilience", climateScore) +
      createScoreCard("Water Sustainability", waterScore) +
      createScoreCard("Economic Impact", economicScore);

    document.getElementById("results").innerHTML =
      createRecommendationCard(
        data.recommendation || "No recommendation returned.",
        data.confidence || 0,
        timelineAgents
      ) +
      createTimeline(timelineAgents) +
      createAgentCard("Planner Agent", agents.planner_agent) +
      createAgentCard("Water Agent", agents.water_agent) +
      createAgentCard("Risk Agent", agents.risk_agent) +
      createAgentCard("Global Impact Agent", agents.global_impact_agent) +
      createSafetyNote(
        data.safety_note ||
        "AI-assisted guidance only. Confirm major decisions with local agricultural experts."
      );

    status.textContent = "Analysis Complete";
  } catch (error) {
    console.error(error);
    status.textContent = "Error";

    showError(
      "Unable to connect to AgriAgent Global API. Verify that your FastAPI backend is running and accessible."
    );
  }
}
