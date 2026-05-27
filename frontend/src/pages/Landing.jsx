import { useNavigate } from 'react-router-dom'
import {
  Activity, Shield, Search, CheckCircle, Users,
  ArrowRight, AlertTriangle, Brain, FileText, Eye
} from 'lucide-react'

const AgentCard = ({ number, name, icon: Icon, description, color }) => (
  <div className="card p-5 flex gap-4">
    <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center flex-shrink-0`}>
      <Icon size={18} className="text-white" />
    </div>
    <div>
      <div className="text-xs text-gray-500 mb-0.5">Agent {number}</div>
      <div className="text-sm font-semibold text-white mb-1">{name}</div>
      <div className="text-xs text-gray-400 leading-relaxed">{description}</div>
    </div>
  </div>
)

const PrincipleStep = ({ step, label, color }) => (
  <div className="flex items-center gap-3">
    <div className={`w-8 h-8 rounded-xl ${color}/20 border ${color}/30 flex items-center justify-center`}>
      <span className={`text-xs font-bold ${color.replace('border-', 'text-')}`}>{step}</span>
    </div>
    <span className="text-sm font-medium text-gray-300">{label}</span>
  </div>
)

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="animate-fade-in space-y-16">
      {/* Hero */}
      <section className="text-center py-12 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 bg-clinical-600/10 border border-clinical-500/20 rounded-full px-4 py-2 text-clinical-400 text-sm font-medium mb-6">
          <Activity size={14} />
          Agentic Clinical Intake & Triage Orchestrator
        </div>

        <h1 className="text-5xl font-bold text-white leading-tight mb-4">
          Evidence-Grounded{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-clinical-400 to-violet-400">
            Intake Preparation
          </span>{' '}
          <br />for Mental Health Review
        </h1>

        <p className="text-xl text-gray-400 leading-relaxed max-w-2xl mx-auto mb-3">
          CareFlow AI converts unstructured intake conversations into structured,
          evidence-grounded reviewer briefs — so qualified professionals can focus
          on clinical judgment, not administrative extraction.
        </p>

        <div className="disclaimer-bar max-w-xl mx-auto mb-8 text-center">
          <AlertTriangle size={13} className="inline mr-1.5 mb-0.5" />
          Not a diagnostic system. All outputs require qualified professional review.
          Built with synthetic data only for hackathon demonstration.
        </div>

        <div className="flex gap-3 justify-center flex-wrap">
          <button
            onClick={() => navigate('/intake/new')}
            className="btn-primary flex items-center gap-2 px-6 py-3"
          >
            Start Demo Intake
            <ArrowRight size={16} />
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-secondary flex items-center gap-2 px-6 py-3"
          >
            Reviewer Dashboard
          </button>
          <button
            onClick={() => navigate('/evaluation')}
            className="btn-secondary flex items-center gap-2 px-6 py-3"
          >
            Evaluation Results
          </button>
        </div>
      </section>

      {/* Core principle */}
      <section className="max-w-3xl mx-auto">
        <h2 className="text-center text-xs font-semibold text-gray-500 uppercase tracking-widest mb-6">
          Core Design Principle
        </h2>
        <div className="card p-6">
          <div className="flex items-center justify-center gap-3 flex-wrap">
            {[
              { step: 'E', label: 'Evidence', color: 'border-clinical-500 text-clinical-400 bg-clinical-500' },
              { step: '→', label: '', color: 'border-transparent text-gray-600 bg-transparent' },
              { step: 'S', label: 'Signal', color: 'border-violet-500 text-violet-400 bg-violet-500' },
              { step: '→', label: '', color: 'border-transparent text-gray-600 bg-transparent' },
              { step: 'V', label: 'Verification', color: 'border-amber-500 text-amber-400 bg-amber-500' },
              { step: '→', label: '', color: 'border-transparent text-gray-600 bg-transparent' },
              { step: 'H', label: 'Human Review', color: 'border-emerald-500 text-emerald-400 bg-emerald-500' },
            ].map((item, i) => (
              item.label ? (
                <div key={i} className="text-center">
                  <div className={`w-10 h-10 rounded-xl ${item.color}/20 border flex items-center justify-center mx-auto mb-2`}>
                    <span className="text-sm font-bold">{item.step}</span>
                  </div>
                  <span className="text-xs text-gray-400">{item.label}</span>
                </div>
              ) : (
                <span key={i} className="text-gray-600 text-xl font-light">→</span>
              )
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-4">
            Every output is traceable to the original conversation.
            Every inference is labeled. Every gap is acknowledged.
          </p>
        </div>
      </section>

      {/* Problem */}
      <section className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-white mb-3">The Problem</h2>
          <p className="text-gray-400 text-sm leading-relaxed mb-4">
            Mental health intake conversations contain critical information distributed across
            free-form natural language. Clinical reviewers manually transform this into structured
            documentation — a time-consuming process prone to:
          </p>
          <ul className="space-y-2 text-sm text-gray-400">
            {[
              'Information omission across long conversations',
              'Inconsistent structuring across reviewers',
              'Unsupported assumptions stated as facts',
              'Missed contradictions in patient statements',
              'Poor visibility into what is unknown vs known',
              'Repetitive administrative extraction work',
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-red-400 mt-0.5">×</span>
                {item}
              </li>
            ))}
          </ul>
        </div>

        <div className="card p-6">
          <h2 className="text-lg font-semibold text-white mb-3">The Solution</h2>
          <p className="text-gray-400 text-sm leading-relaxed mb-4">
            CareFlow AI prepares a structured, evidence-grounded intake brief for the
            qualified human reviewer — reducing extraction burden while maintaining
            complete transparency about uncertainty.
          </p>
          <ul className="space-y-2 text-sm text-gray-400">
            {[
              'Dynamic intake interview covering all required areas',
              'Safety-relevant signal identification with evidence',
              'Structured extraction with explicit/inferred labels',
              'Automated contradiction and gap detection',
              'Verification loop before human handoff',
              'Complete evidence trace for every finding',
              'Human review gate — no autonomous decisions',
            ].map((item, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-emerald-400 mt-0.5">✓</span>
                {item}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Agent architecture */}
      <section>
        <h2 className="text-center text-lg font-semibold text-white mb-6">5-Agent Pipeline</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AgentCard number={1} name="Intake Interviewer" icon={Brain}
            description="Conducts dynamic conversations, adapting questions to cover missing intake areas."
            color="bg-clinical-600" />
          <AgentCard number={2} name="Safety Signal Extractor" icon={AlertTriangle}
            description="Identifies 10 predefined safety-relevant signal categories with evidence. Not a diagnostic tool."
            color="bg-red-700" />
          <AgentCard number={3} name="Clinical Structuring Agent" icon={FileText}
            description="Converts conversation to structured fields with explicit/inferred/unknown status."
            color="bg-violet-700" />
          <AgentCard number={4} name="Verification Agent" icon={CheckCircle}
            description="Checks for unsupported claims, hallucinations, contradictions. Retries up to 3 times."
            color="bg-amber-700" />
          <AgentCard number={5} name="Triage Orchestrator" icon={Activity}
            description="Coordinates all agents, manages state, produces the final reviewer-ready brief."
            color="bg-emerald-700" />
          <div className="card p-5 flex gap-4 border-clinical-500/20">
            <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center flex-shrink-0">
              <Eye size={18} className="text-gray-400" />
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-0.5">Human Gate</div>
              <div className="text-sm font-semibold text-white mb-1">Qualified Reviewer</div>
              <div className="text-xs text-gray-400 leading-relaxed">
                All consequential decisions remain with the human reviewer.
                CareFlow prepares — it does not decide.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What the system never does */}
      <section className="card p-6 border-red-500/10 bg-red-500/5">
        <h2 className="text-base font-semibold text-white mb-3 flex items-center gap-2">
          <Shield size={16} className="text-red-400" />
          What CareFlow AI Never Does
        </h2>
        <div className="grid sm:grid-cols-2 gap-2 text-sm text-gray-400">
          {[
            'Diagnose mental health conditions',
            'Make autonomous clinical decisions',
            'Claim a patient is safe or unsafe',
            'Prescribe or recommend treatment',
            'Contact emergency services autonomously',
            'Contact family or third parties autonomously',
            'Label outputs as final clinical judgments',
            'Use real patient data (synthetic only)',
          ].map((item, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-red-500/60 mt-0.5">⊘</span>
              {item}
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
