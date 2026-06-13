const API_URL =
  "https://fluffy-doodle-x54vgjjjj5wr3pg66-8000.app.github.dev/multi-agent-analysis";

let latestAnalysis = null;

const menuBtn = document.getElementById("menuBtn");
const mobileMenu = document.getElementById("mobileMenu");

if (menuBtn && mobileMenu) {
  menuBtn.addEventListener("click", () => {
    mobileMenu.classList.toggle("hidden");
  });
}

function getScore(text, label) {
  if (!text) return 0;

  const match = text.match(new RegExp(`${label}:\\s*(\\d+)`, "i"));
  return match ? parseInt(match[1], 10) : 0;
}

function getConfidenceLevel(score) {
  if (score >= 80) return "High";
  if (score >= 65) return "Medium";
  return "Low";
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

function createConfidenceCard(title, value, note) {
  return `
    <div class="score-card confidence-card">
      <p>${title}</p>
      <strong>${value}</strong>
      <span>${note}</span>
    </div>
  `;
}

function createConfidenceGrid(data) {
  const overall = data.confidence || 0;
  const seasonLevel = data.season_context ? "High" : "Medium";

  const safetyLevel =
    data.risk_level === "Low"
      ? "High"
      : data.risk_level === "Medium"
      ? "Medium"
      : "Low";

  return (
    createConfidenceCard("Overall Confidence", `${overall}%`, getConfidenceLevel(overall)) +
    createConfidenceCard("Season Context", seasonLevel, "Location-aware estimate") +
    createConfidenceCard("Safety Confidence", safetyLevel, `Risk level: ${data.risk_level || "Unknown"}`) +
    createConfidenceCard("Data Grounding", "Medium", "AI + local verification")
  );
}

function createRecommendationCard(recommendation, confidence, agents) {
  const reasons = (agents || [])
    .map(agent => `<li>${agent.finding}</li>`)
    .join("");

  return `
    <div class="recommendation-card">
      <h3>Executive Recommendation</h3>

      <p><strong>Best action:</strong> ${recommendation || "No recommendation returned."}</p>
      <p><strong>Confidence:</strong> ${confidence || 0}%</p>

      <h4>Why this recommendation?</h4>
      <ul>${reasons}</ul>
    </div>
  `;
}

function createTimeline(agents) {
  return `
    <div class="agent-card">
      <h3>Agent Execution Timeline</h3>

      <div class="timeline">
        ${(agents || [])
          .map(
            (agent, index) => `
              <div class="timeline-step timeline-animated" style="animation-delay:${index * 0.12}s">
                <strong>${agent.name}</strong>
                <span>${agent.status}</span>
                <p>${agent.finding}</p>
              </div>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}

function createSeasonCard(seasonContext) {
  if (!seasonContext) return "";

  return `
    <div class="agent-card">
      <h3>Season & Location Intelligence</h3>

      <pre>Region: ${seasonContext.hemisphere || "Unknown"}
Estimated season: ${seasonContext.current_season_estimate || "Unknown"}

${seasonContext.seasonal_guidance || "No seasonal guidance returned."}</pre>
    </div>
  `;
}

function createRiskCard(data) {
  return `
    <div class="agent-card">
      <h3>Reliability & Safety Check</h3>

      <pre>Risk level: ${data.risk_level || "Unknown"}

Safety warning:
${data.safety_warning || "No safety warning returned."}</pre>
    </div>
  `;
}

function createListCard(title, items) {
  if (!items || !items.length) return "";

  return `
    <div class="agent-card">
      <h3>${title}</h3>

      <ul class="clean-list">
        ${items.map(item => `<li>${item}</li>`).join("")}
      </ul>
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
      ${note || "AgriAgent provides AI-assisted guidance only. Confirm major farming decisions with local experts."}
    </div>
  `;
}

function showLoading() {
  const confidenceGrid = document.getElementById("confidenceGrid");
  const pdfActions = document.getElementById("pdfActions");

  if (confidenceGrid) confidenceGrid.innerHTML = "";
  if (pdfActions) pdfActions.classList.add("hidden");

  document.getElementById("results").innerHTML = `
    <div class="agent-card">
      <h3>Running Multi-Agent Analysis</h3>

      <div class="timeline">
        <div class="timeline-step timeline-animated">
          <strong>Season and Location Agent</strong>
          <span>running</span>
          <p>Inferring regional season and climate context.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.12s">
          <strong>Input Validation Agent</strong>
          <span>running</span>
          <p>Checking farm profile quality.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.24s">
          <strong>Safety Agent</strong>
          <span>running</span>
          <p>Evaluating risky farming decisions.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.36s">
          <strong>Planner Agent</strong>
          <span>running</span>
          <p>Creating farm strategy.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.48s">
          <strong>Water Agent</strong>
          <span>running</span>
          <p>Designing water resilience actions.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.60s">
          <strong>Risk Agent</strong>
          <span>running</span>
          <p>Assessing climate, pest, and market risks.</p>
        </div>

        <div class="timeline-step timeline-animated" style="animation-delay:0.72s">
          <strong>Global Impact Agent</strong>
          <span>running</span>
          <p>Calculating impact scores.</p>
        </div>
      </div>
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
  const confidenceGrid = document.getElementById("confidenceGrid");
  const pdfActions = document.getElementById("pdfActions");

  status.textContent = "Running Analysis";
  scoreGrid.innerHTML = "";
  if (confidenceGrid) confidenceGrid.innerHTML = "";
  if (pdfActions) pdfActions.classList.add("hidden");

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
    latestAnalysis = data;

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

    if (confidenceGrid) {
      confidenceGrid.innerHTML = createConfidenceGrid(data);
    }

    document.getElementById("results").innerHTML =
      createRecommendationCard(data.recommendation, data.confidence, timelineAgents) +
      createSeasonCard(data.season_context) +
      createRiskCard(data) +
      createTimeline(timelineAgents) +
      createAgentCard("Planner Agent", agents.planner_agent) +
      createAgentCard("Water Agent", agents.water_agent) +
      createAgentCard("Risk Agent", agents.risk_agent) +
      createAgentCard("Global Impact Agent", agents.global_impact_agent) +
      createListCard("Assumptions", data.assumptions) +
      createListCard("Local Verification Steps", data.local_verification_steps) +
      createSafetyNote(data.safety_note);

    if (pdfActions) pdfActions.classList.remove("hidden");

    status.textContent = "Analysis Complete";
  } catch (error) {
    console.error(error);
    latestAnalysis = null;
    status.textContent = "Error";

    if (pdfActions) pdfActions.classList.add("hidden");

    showError(
      "Unable to connect to AgriAgent Global API. Verify that your FastAPI backend is running and accessible."
    );
  }
}

function safeText(value) {
  return value ? String(value) : "Not available";
}

function addWrappedText(doc, text, x, y, maxWidth, lineHeight) {
  const lines = doc.splitTextToSize(safeText(text), maxWidth);

  for (const line of lines) {
    if (y > 275) {
      doc.addPage();
      y = 20;
    }

    doc.text(line, x, y);
    y += lineHeight;
  }

  return y;
}

function addSection(doc, title, content, y) {
  if (y > 255) {
    doc.addPage();
    y = 20;
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.text(title, 15, y);
  y += 8;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  y = addWrappedText(doc, content, 15, y, 180, 6);
  y += 6;

  return y;
}

function downloadPDFReport() {
  if (!latestAnalysis) {
    alert("Run an analysis before downloading the report.");
    return;
  }

  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert("PDF library failed to load. Check your internet connection and try again.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();

  const profile = latestAnalysis.farmer_profile || {};
  const agents = latestAnalysis.agent_results || {};

  let y = 18;

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("AgriAgent Global Advisory Report", 15, y);

  y += 10;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 15, y);

  y += 12;

  y = addSection(
    doc,
    "Farmer Profile",
    `Location: ${profile.location}
Farming Goal: ${profile.farming_goal}
Farm Size: ${profile.farm_size}
Main Challenge: ${profile.challenge}`,
    y
  );

  y = addSection(
    doc,
    "Executive Recommendation",
    `Recommendation: ${latestAnalysis.recommendation}
Confidence: ${latestAnalysis.confidence}%
Risk Level: ${latestAnalysis.risk_level}
Safety Warning: ${latestAnalysis.safety_warning}`,
    y
  );

  y = addSection(
    doc,
    "Season and Location Intelligence",
    `Region: ${latestAnalysis.season_context?.hemisphere}
Estimated Season: ${latestAnalysis.season_context?.current_season_estimate}
Guidance: ${latestAnalysis.season_context?.seasonal_guidance}`,
    y
  );

  y = addSection(doc, "Planner Agent", agents.planner_agent, y);
  y = addSection(doc, "Water Agent", agents.water_agent, y);
  y = addSection(doc, "Risk Agent", agents.risk_agent, y);
  y = addSection(doc, "Global Impact Agent", agents.global_impact_agent, y);

  y = addSection(
    doc,
    "Assumptions",
    (latestAnalysis.assumptions || []).map(item => `- ${item}`).join("\n"),
    y
  );

  y = addSection(
    doc,
    "Local Verification Steps",
    (latestAnalysis.local_verification_steps || [])
      .map(item => `- ${item}`)
      .join("\n"),
    y
  );

  y = addSection(
    doc,
    "Safety Disclaimer",
    latestAnalysis.safety_note,
    y
  );

  doc.save("agriagent-advisory-report.pdf");
}
