import { Shield, Activity, AlertTriangle, FileText, Users } from 'lucide-react'

export default function About() {
  return (
    <div className="animate-fade-in max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">About CareFlow AI</h1>
        <p className="text-gray-400 text-sm leading-relaxed">
          CareFlow AI is an agentic clinical intake preparation system built for the micro1 Hackathon.
          It demonstrates how multi-agent AI can reduce administrative burden in mental health intake workflows
          while maintaining evidence integrity and human oversight.
        </p>
      </div>

      {/* Ethical principles */}
      <div className="card p-6">
        <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Shield size={16} className="text-clinical-400" />
          Ethical Design Principles
        </h2>
        <div className="space-y-3 text-sm">
          {[
            ['Evidence transparency', 'Every claim is traceable to a specific turn in the conversation. Inferences are labeled as inferences.'],
            ['Uncertainty acknowledgment', 'What was not established is always stated explicitly. The system never claims false certainty.'],
            ['Human primacy', 'All consequential decisions remain with qualified human reviewers. CareFlow prepares — it does not decide.'],
            ['No diagnostic language', 'The system never uses diagnostic terminology or presents outputs as clinical conclusions.'],
            ['Conservative by design', 'Safety signals are flagged for reviewer attention, not assessed clinically.'],
          ].map(([title, desc]) => (
            <div key={title}>
              <div className="text-white font-medium mb-0.5">{title}</div>
              <div className="text-gray-400">{desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Technical architecture */}
      <div className="card p-6">
        <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <Activity size={16} className="text-clinical-400" />
          Technical Architecture
        </h2>
        <div className="grid sm:grid-cols-2 gap-4 text-sm text-gray-400">
          <div>
            <div className="text-white font-medium mb-1">Backend</div>
            <ul className="space-y-0.5 text-xs">
              <li>Flask + SQLAlchemy</li>
              <li>5-agent orchestrator pattern</li>
              <li>Groq (llama-3.3-70b-versatile)</li>
              <li>SQLite for hackathon demo</li>
              <li>Full JSON audit trail</li>
            </ul>
          </div>
          <div>
            <div className="text-white font-medium mb-1">Frontend</div>
            <ul className="space-y-0.5 text-xs">
              <li>React + Vite</li>
              <li>Tailwind CSS</li>
              <li>Real-time interview interface</li>
              <li>Evidence Explorer</li>
              <li>Evaluation Dashboard</li>
            </ul>
          </div>
          <div>
            <div className="text-white font-medium mb-1">Evaluation</div>
            <ul className="space-y-0.5 text-xs">
              <li>12 synthetic evaluation cases</li>
              <li>Gold-standard annotations</li>
              <li>Reviewer-Ready Score metric</li>
              <li>Baseline vs agent comparison</li>
              <li>Agent trajectory logging</li>
            </ul>
          </div>
          <div>
            <div className="text-white font-medium mb-1">Safety</div>
            <ul className="space-y-0.5 text-xs">
              <li>10-signal safety taxonomy</li>
              <li>Never makes clinical decisions</li>
              <li>Verification loop (max 3 retries)</li>
              <li>Human review gate on all outputs</li>
              <li>Synthetic data only</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Limitations */}
      <div className="card p-6 border-amber-500/10 bg-amber-500/3">
        <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
          <AlertTriangle size={16} className="text-amber-400" />
          Limitations & Scope
        </h2>
        <ul className="space-y-2 text-sm text-gray-400">
          {[
            'Demonstration only — built on synthetic data for hackathon evaluation',
            'Not suitable for real clinical use without extensive validation',
            'LLM outputs can be incorrect and require verification',
            'Safety signal detection is not equivalent to clinical risk assessment',
            'Groq API rate limits may affect processing times',
            'Evaluation scoring is approximate — not clinically validated',
          ].map((item, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-amber-500/50 flex-shrink-0 mt-0.5">⚠</span>
              {item}
            </li>
          ))}
        </ul>
      </div>

      {/* Hackathon */}
      <div className="card p-6">
        <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
          <Users size={16} className="text-clinical-400" />
          Hackathon Context
        </h2>
        <p className="text-sm text-gray-400 leading-relaxed">
          Built for the micro1 Agentic Workflows Hackathon. This project demonstrates a meaningful real-world
          bottleneck (mental health intake inefficiency), purposeful use of multiple agents, measurable
          improvement over a single-prompt baseline, and reproducible evaluation with synthetic cases.
          All source code, evaluation cases, and trajectories are available for inspection.
        </p>
        <div className="mt-3 text-xs text-gray-600">
          Note: CareFlow AI is distinct from MindSphere, a separate ML classification project.
          CareFlow AI is new, purpose-built work for this hackathon.
        </div>
      </div>
    </div>
  )
}
