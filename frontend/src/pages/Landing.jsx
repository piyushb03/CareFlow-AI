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
