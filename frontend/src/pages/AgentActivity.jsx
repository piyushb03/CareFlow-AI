import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Activity, Shield, FileText, CheckCircle, AlertTriangle, RotateCcw, ArrowRight, Loader } from 'lucide-react'
import { getCase } from '../services/api'

const AGENT_STEPS = [
  { key: 'safety_signal_agent', label: 'Safety Signal Extractor', icon: Shield, description: 'Analyzing safety-relevant language' },
  { key: 'structuring_agent', label: 'Clinical Structuring Agent', icon: FileText, description: 'Structuring intake information' },
  { key: 'verification_agent', label: 'Verification Agent', icon: CheckCircle, description: 'Verifying against original conversation' },
  { key: 'orchestrator', label: 'Triage Orchestrator', icon: Activity, description: 'Producing reviewer-ready brief' },
]

const StatusIcon = ({ status }) => {
  if (status === 'complete') return <CheckCircle size={14} className="text-emerald-400" />
  if (status === 'running') return <Loader size={14} className="text-clinical-400 animate-spin" />
  if (status === 'warning') return <AlertTriangle size={14} className="text-amber-400" />
  if (status === 'retry') return <RotateCcw size={14} className="text-amber-400 animate-spin" />
  return <div className="w-3.5 h-3.5 rounded-full border border-gray-700" />
}

export default function AgentActivity() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [agentStates, setAgentStates] = useState({})
  const [verificationStatus, setVerificationStatus] = useState(null)
  const [retryCount, setRetryCount] = useState(0)
  const [done, setDone] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [logs, setLogs] = useState([])

  useEffect(() => {
    simulateAgentProgress()
    const poll = setInterval(checkStatus, 3000)
    return () => clearInterval(poll)
  }, [caseId])

  const addLog = (msg) => setLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg }])

  const simulateAgentProgress = async () => {
    // Simulate agent progress while polling actual status
    const steps = ['safety_signal_agent', 'structuring_agent', 'verification_agent', 'orchestrator']
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i)
      setAgentStates(prev => ({ ...prev, [steps[i]]: 'running' }))
      addLog(`${AGENT_STEPS[i].label} started`)
      await new Promise(r => setTimeout(r, 2500))
      setAgentStates(prev => ({ ...prev, [steps[i]]: 'complete' }))
      addLog(`${AGENT_STEPS[i].label} completed`)
    }
  }

  const checkStatus = async () => {
    try {
      const res = await getCase(caseId)
      const c = res.data
      setCaseData(c)
      if (c.status === 'ready_for_review' || c.status === 'reviewed') {
        setDone(true)
        setVerificationStatus(c.verification_status)
      }
    } catch (err) {
      // ignore poll errors
    }
  }

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white mb-1">Agent Processing</h1>
        <p className="text-gray-400 text-sm">
          Multi-agent pipeline running — Safety → Structuring → Verification → Brief
        </p>
      </div>

      {/* Agent steps */}
      <div className="card p-6 mb-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-4">Agent Activity</h2>
        <div className="space-y-3">
          {AGENT_STEPS.map((step, i) => {
            const state = agentStates[step.key] || 'pending'
            const Icon = step.icon
            return (
              <div key={step.key} className={`agent-activity-item transition-all duration-300 ${state === 'running' ? 'border-clinical-500/20 bg-clinical-500/5' : ''}`}>
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  state === 'complete' ? 'bg-emerald-500/10' : state === 'running' ? 'bg-clinical-500/10' : 'bg-white/3'
                }`}>
                  <Icon size={15} className={state === 'complete' ? 'text-emerald-400' : state === 'running' ? 'text-clinical-400' : 'text-gray-600'} />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${state === 'complete' ? 'text-white' : state === 'running' ? 'text-clinical-200' : 'text-gray-600'}`}>
                      {step.label}
                    </span>
                    <StatusIcon status={state} />
                    {step.key === 'verification_agent' && retryCount > 0 && (
                      <span className="badge-medium text-xs">Retry {retryCount}</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Verification status */}
      {verificationStatus && (
        <div className={`card p-4 mb-4 border ${verificationStatus === 'passed' ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-amber-500/20 bg-amber-500/5'}`}>
          <div className="flex items-center gap-2">
            {verificationStatus === 'passed'
              ? <CheckCircle size={15} className="text-emerald-400" />
              : <AlertTriangle size={15} className="text-amber-400" />
            }
            <span className={`text-sm font-medium ${verificationStatus === 'passed' ? 'text-emerald-300' : 'text-amber-300'}`}>
              Verification: {verificationStatus === 'passed' ? 'Passed' : 'Requires Human Review'}
            </span>
          </div>
        </div>
      )}

      {/* Activity log */}
      <div className="card p-4 mb-4">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Activity Log</h2>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-2 text-xs">
              <span className="text-gray-600 font-mono flex-shrink-0">{log.time}</span>
              <span className="text-gray-400">{log.msg}</span>
            </div>
          ))}
          {logs.length === 0 && <p className="text-gray-600 text-xs">Processing...</p>}
        </div>
      </div>

      {/* Done */}
      {done && (
        <div className="card p-5 border-clinical-500/20 bg-clinical-500/5 animate-slide-up">
          <h3 className="text-clinical-300 font-semibold mb-2 flex items-center gap-2">
            <CheckCircle size={16} className="text-clinical-400" />
            Ready for Human Review
          </h3>
          <p className="text-gray-400 text-sm mb-4">
            The intake brief has been prepared and is awaiting qualified reviewer assessment.
          </p>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => navigate(`/cases/${caseId}`)} className="btn-primary flex items-center gap-2 text-sm">
              View Case Brief <ArrowRight size={14} />
            </button>
            <button onClick={() => navigate(`/cases/${caseId}/evidence`)} className="btn-secondary text-sm">
              Evidence Explorer
            </button>
            <button onClick={() => navigate(`/cases/${caseId}/verification`)} className="btn-secondary text-sm">
              Verification Results
            </button>
          </div>
        </div>
      )}

      {!done && (
        <div className="text-center text-gray-500 text-xs animate-pulse">
          Processing... This may take 30-60 seconds
        </div>
      )}
    </div>
  )
}
