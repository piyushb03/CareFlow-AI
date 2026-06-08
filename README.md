# CareFlow AI 🏥

**Agentic Clinical Intake & Triage Orchestrator**

> *AI-assisted intake preparation for mental health professionals — not a diagnostic system.*

---

## ⚠️ Important Disclaimer

CareFlow AI is a **hackathon demonstration system** built on **synthetic data only**.

- It is **not a clinical tool** and must not be used with real patients
- It does **not diagnose** mental health conditions
- It does **not make autonomous clinical decisions**
- All outputs require review by a **qualified mental health professional**
- This system never contacts emergency services, family members, or third parties

---

## What It Does

CareFlow AI addresses a real bottleneck in mental health care: the **administrative burden of intake documentation**. Clinicians spend significant time manually converting unstructured intake conversations into structured documentation — work that is tedious, inconsistent, and prone to errors.

CareFlow AI uses a **5-agent orchestrator pipeline** to:

1. **Conduct** a dynamic intake interview (AI asks structured questions, adapts to answers)
2. **Extract** safety-relevant signals with direct evidence citations
3. **Structure** all clinical fields with explicit/inferred/unknown labels
4. **Verify** every claim against the original conversation (max 3 retries)
5. **Produce** a reviewer-ready brief with full evidence trace — for human review

The human reviewer makes all consequential decisions. CareFlow prepares — it does not decide.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              CareFlow AI Pipeline                    │
│                                                     │
│  ┌──────────┐  ┌────────┐  ┌───────────┐           │
│  │  Intake  │→ │Safety  │→ │Structuring│           │
│  │  Agent   │  │Signal  │  │  Agent    │           │
│  │  (A1)   │  │ Agent  │  │   (A3)   │           │
│  └──────────┘  │  (A2) │  └───────────┘           │
│                └────────┘         │                 │
│                              ┌────▼──────┐          │
│                              │Verification│          │
│                              │  Agent    │          │
│                              │  (A4)   │          │
│                              └────┬──────┘          │
│                 ┌─────────────────▼──────────┐      │
│                 │     Triage Orchestrator     │      │
│                 │          (A5)              │      │
│                 └─────────────────┬──────────┘      │
│                                   │                 │
│                            ┌──────▼──────┐          │
│                            │   HUMAN     │          │
│                            │  REVIEWER   │          │
│                            └─────────────┘          │
└─────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Role | Key Behavior |
|-------|------|-------------|
| **Intake Agent** | Conducts dynamic interview | Adapts questions to cover missing areas |
| **Safety Signal Extractor** | Identifies 10 safety signals | Never diagnoses — flags for reviewer attention only |
| **Clinical Structuring Agent** | Structures all fields | Labels every field as explicit/inferred/unknown |
| **Verification Agent** | Validates all claims | Max 3 retries; flags unsupported claims, contradictions |
| **Triage Orchestrator** | Coordinates pipeline | Manages state, produces final brief, enforces human gate |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+, Flask 3.0, SQLAlchemy 2.0 |
| LLM Provider | Groq (`llama-3.3-70b-versatile`) or Google Gemini |
| Database | SQLite (hackathon) |
| Frontend | React 18 + Vite, Tailwind CSS |
| Evaluation | Custom `Reviewer-Ready Score` metric (0-100) |
| PDF Reports | ReportLab |

---

## Judging Criteria Mapping

| Criterion | Points | How CareFlow Addresses It |
|-----------|--------|--------------------------|
| Problem & User Value | 15 | Real bottleneck (intake documentation time), clear user (clinical reviewers), measured impact |
| Agent Solution & Engineering | 30 | 5-agent orchestrator, verification loop, trajectory logging, evidence chain architecture |
| End-to-End Quality | 20 | Full pipeline from interview → verified brief → human review gate |
| Measured Improvement | 15 | Baseline vs multi-agent comparison on 12 synthetic cases with `Reviewer-Ready Score` |
| Reproducibility | 15 | Synthetic cases, gold annotations, `.env.example`, `requirements.txt`, seeded evaluation |
| Hot Take / Insights | 5 | Human-in-the-loop is not a limitation — it's the ethical design requirement |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Groq API key (free) OR a Google Gemini API key (free)

### 1. Clone & Setup

```bash
git clone <repo-url>
cd careflow-ai
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API key (see below)
```

### 3. Configure API Key

Edit `.env` — choose **one** provider:

```env
# Option A: Groq (recommended — free, ultra-fast)
# Get key at: https://console.groq.com
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here

# Option B: Google Gemini (free)
# Get key at: https://aistudio.google.com/app/apikey
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza_your_key_here
```

### 4. Start Backend

```bash
python run.py
# → Running on http://localhost:5000
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
# → Running on http://localhost:5173
```

### 6. Open the App

→ **http://localhost:5173**

---

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Landing | `/` | Overview, agent architecture, safety principles |
| New Intake | `/intake/new` | Create a new case with disclaimers |
| Live Interview | `/intake/:id/conversation` | Real-time AI interview with coverage tracker |
| Agent Activity | `/cases/:id/processing` | Live agent progress visualization |
| Reviewer Dashboard | `/dashboard` | All cases with filters and status |
| Case Detail | `/cases/:id` | Full reviewer brief, safety signals, evidence |
| Evidence Explorer | `/cases/:id/evidence` | Click any field to see full evidence chain |
| Verification Results | `/cases/:id/verification` | Issues found by verification agent |
| Evaluation Dashboard | `/evaluation` | Baseline vs agent comparison metrics |
| About & Safety | `/about` | Ethical principles, limitations, architecture |

---

## API Endpoints

```
GET  /health                           — Health check
POST /api/cases                        — Create case
GET  /api/cases                        — List cases
GET  /api/cases/:id                    — Get case details
POST /api/cases/:id/start-interview    — Start intake interview
POST /api/cases/:id/messages           — Send patient message, get next question
POST /api/cases/:id/process            — Run 5-agent pipeline
GET  /api/cases/:id/conversation       — Get conversation turns
GET  /api/cases/:id/evidence           — Get extracted fields with evidence
GET  /api/cases/:id/verification       — Get verification issues
GET  /api/cases/:id/trajectory         — Get agent trajectory (for judges)
GET  /api/cases/:id/audit              — Full audit trail
POST /api/cases/:id/approve            — Reviewer approves
POST /api/cases/:id/reject             — Reviewer rejects
GET  /api/evaluation/results           — Get evaluation results
POST /api/evaluation/run               — Run evaluation (mode: baseline|agent)
```

---

## Evaluation

CareFlow AI includes a rigorous evaluation harness:

- **12 synthetic intake cases** with varying complexity
- **Gold-standard annotations** for each case
- **Custom `Reviewer-Ready Score`** (0-100) across 6 weighted domains:
  - Evidence extraction accuracy (25%)
  - Safety signal identification (25%)
  - Evidence attribution (20%)
  - Contradiction detection (10%)
  - Missing information flagging (10%)
  - Unsupported claims (10%)

### Run Evaluation

```bash
# Run baseline (single-prompt comparison)
python -m evaluation.run_baseline

# Run agent pipeline evaluation
python -m evaluation.run_agent

# Generate comparison report
python -m evaluation.evaluate
```

Or use the Evaluation Dashboard at `/evaluation`.

---

## Project Structure

```
careflow-ai/
├── backend/
│   ├── app.py                          # Flask factory
│   ├── extensions.py                   # SQLAlchemy instance
│   ├── models/                         # SQLAlchemy models
│   │   ├── case.py                     # Central case record
│   │   ├── conversation.py             # Conversation turns
│   │   ├── extracted_field.py          # Structured fields with evidence
│   │   ├── safety_signal.py            # Safety signals (not diagnoses)
│   │   ├── verification.py             # Verification issues
│   │   ├── review.py                   # Reviewer decisions
│   │   ├── agent_run.py                # Agent execution records
│   │   └── audit.py                    # Immutable audit log
│   ├── routes/
│   │   ├── cases.py                    # Case management API
│   │   ├── evaluation.py               # Evaluation API
│   │   └── health.py                   # Health check
│   ├── schemas/
│   │   ├── intake_schema.py            # Intake field taxonomy
│   │   └── safety_taxonomy.py          # 10 safety signal definitions
│   └── services/
│       ├── agents/
│       │   ├── base.py                 # Agent base class
│       │   ├── intake_agent.py         # Agent 1: Dynamic interviewer
│       │   ├── safety_agent.py         # Agent 2: Signal extractor
│       │   ├── structuring_agent.py    # Agent 3: Field structurer
│       │   └── verification_agent.py   # Agent 4: Claim verifier
│       ├── llm/
│       │   └── client.py               # Groq + Gemini provider
│       └── orchestration/
│           └── orchestrator.py         # Agent 5: Triage orchestrator
├── evaluation/
│   ├── cases/                          # 12 synthetic test cases
│   ├── gold/                           # Gold standard annotations
│   ├── scorer.py                       # Reviewer-Ready Score engine
│   ├── run_baseline.py                 # Baseline runner
│   ├── run_agent.py                    # Agent eval runner
│   └── evaluate.py                     # Comparison report generator
├── prompts/
│   ├── intake_agent.md                 # Intake Agent prompt (versioned)
│   ├── safety_agent.md                 # Safety Signal prompt
│   ├── structuring_agent.md            # Structuring Agent prompt
│   └── verification_agent.md          # Verification Agent prompt
├── frontend/
│   ├── src/
│   │   ├── pages/                      # 10 React pages
│   │   ├── components/                 # Layout, shared components
│   │   └── services/api.js             # API client
│   ├── tailwind.config.js
│   └── vite.config.js
├── trajectories/                       # Agent trajectory logs (per case)
├── reports/                            # Generated PDF reports
├── run.py                              # Backend entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Safety & Ethical Design

CareFlow AI is designed with safety-first principles:

| Principle | Implementation |
|-----------|---------------|
| **Evidence transparency** | Every field is cited to a specific conversation turn |
| **Uncertainty acknowledgment** | Unknown fields are always explicitly labeled |
| **Human primacy** | No autonomous decisions — all outputs go to human reviewer |
| **No diagnostic language** | Agents never use diagnostic terminology |
| **Conservative flagging** | Safety signals go to reviewer, not to an autonomous action |
| **No real data** | Only synthetic data in this demonstration |

### What the system never does

- Diagnose mental health conditions
- Make autonomous clinical decisions
- Claim a patient is safe or unsafe
- Prescribe or recommend treatment
- Contact emergency services
- Contact family or third parties
- Label outputs as final clinical judgments

---

## Reproducibility

All evaluation cases are synthetic and seeded:

```bash
# Reproduce the full evaluation
python -m evaluation.run_baseline --seed 42
python -m evaluation.run_agent --seed 42
python -m evaluation.evaluate --output evaluation/results/
```

Agent trajectories are saved to `trajectories/<case_id>.json` for full inspection.

---

## Development

```bash
# Run tests
pytest tests/ -v

# Type checking
python -m mypy backend/

# Lint
python -m flake8 backend/
```

---

## License

MIT — Hackathon demonstration only. Not for clinical use.

---

*Built for the micro1 Agentic Workflows Hackathon — CareFlow AI demonstrates that meaningful AI-in-healthcare requires evidence grounding, uncertainty acknowledgment, and irreplaceable human oversight.*
