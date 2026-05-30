import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, FileText, MessageSquare, ArrowRight } from 'lucide-react'
import { createCase } from '../services/api'

export default function NewIntake() {
  const navigate = useNavigate()
  const [caseRef, setCaseRef] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleStart = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await createCase({ case_ref: caseRef || undefined })
      navigate(`/intake/${res.data.id}/conversation`)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create case')
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white mb-2">New Intake</h1>
        <p className="text-gray-400 text-sm">
          Begin an AI-assisted intake interview. The conversation will be structured,
          verified, and prepared for qualified professional review.
        </p>
      </div>

      {/* Disclaimer */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-5 mb-6">
        <div className="flex items-start gap-3">
          <AlertTriangle size={18} className="text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="text-amber-300 font-semibold text-sm mb-2">Important — Please Read</h2>
            <ul className="text-amber-200/70 text-xs space-y-1.5">
              <li>• This is an <strong>AI-assisted intake preparation tool</strong>, not a clinical assessment.</li>
              <li>• CareFlow AI does <strong>not diagnose</strong> mental health conditions.</li>
              <li>• All outputs require review by a <strong>qualified mental health professional</strong>.</li>
              <li>• This demonstration uses <strong>synthetic data only</strong>. Do not enter real patient information.</li>
              <li>• The system will not make clinical decisions or contact emergency services.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Case Reference */}
      <div className="card p-6 mb-4">
        <h2 className="text-sm font-semibold text-white mb-4">Case Reference (Optional)</h2>
        <input
          type="text"
          value={caseRef}
          onChange={e => setCaseRef(e.target.value)}
          placeholder="e.g. CASE-2026-001 (leave blank for auto-generated)"
          className="input-field"
        />
        <p className="text-xs text-gray-500 mt-2">
          Used for reference only. No identifying information required.
        </p>
      </div>

      {/* What happens next */}
      <div className="card p-6 mb-6">
        <h2 className="text-sm font-semibold text-white mb-4">What will happen</h2>
        <div className="space-y-3">
          {[
            { icon: MessageSquare, label: 'Live interview', desc: 'The Intake Agent will ask structured questions, adapting based on your answers.' },
            { icon: FileText, label: 'Processing', desc: 'Three specialized agents extract, analyze, and verify the information.' },
            { icon: AlertTriangle, label: 'Review preparation', desc: 'A structured brief is prepared for qualified professional review.' },
          ].map(({ icon: Icon, label, desc }, i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-clinical-600/20 flex items-center justify-center flex-shrink-0">
                <Icon size={15} className="text-clinical-400" />
              </div>
              <div>
                <div className="text-sm font-medium text-white">{label}</div>
                <div className="text-xs text-gray-400">{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleStart}
        disabled={loading}
        className="btn-primary w-full flex items-center justify-center gap-2 py-3 text-base"
      >
        {loading ? 'Creating case...' : 'Begin Intake Interview'}
        {!loading && <ArrowRight size={16} />}
      </button>
    </div>
  )
}
