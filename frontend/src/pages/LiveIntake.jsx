import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Send, Activity, CheckCircle, AlertCircle, Loader, ArrowRight } from 'lucide-react'
import { startInterview, sendMessage, processCase } from '../services/api'

const INTAKE_AREAS = [
  'presenting_concern', 'symptom_description', 'functional_impact',
  'safety', 'history', 'treatment_and_medications', 'substances',
  'support_and_context', 'goals'
]

const AREA_LABELS = {
  presenting_concern: 'Presenting Concern',
  symptom_description: 'Symptom Description',
  functional_impact: 'Functional Impact',
  safety: 'Safety',
  history: 'Relevant History',
  treatment_and_medications: 'Treatment & Medications',
  substances: 'Substances',
  support_and_context: 'Support & Context',
  goals: 'Goals',
}

const REQUIRED_AREAS = ['presenting_concern', 'symptom_description', 'functional_impact', 'safety']

export default function LiveIntake() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [turns, setTurns] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [coveredAreas, setCoveredAreas] = useState([])
  const [isComplete, setIsComplete] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    initInterview()
  }, [caseId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [turns])

  const initInterview = async () => {
    try {
      const res = await startInterview(caseId)
      const agentTurn = res.data.agent_turn
      setTurns([{
        role: 'agent',
        content: agentTurn.content,
        turn_index: agentTurn.turn_index,
        intake_area: agentTurn.intake_area,
      }])
      setLoading(false)
      setTimeout(() => inputRef.current?.focus(), 100)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to start interview')
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || sending || isComplete) return
    const userInput = input.trim()
    setInput('')
    setSending(true)
    setError(null)

    // Optimistic patient turn
    const newTurnIdx = (turns[turns.length - 1]?.turn_index || 0) + 1
    setTurns(prev => [...prev, { role: 'patient', content: userInput, turn_index: newTurnIdx }])

    try {
      const res = await sendMessage(caseId, userInput, coveredAreas)
      const data = res.data

      if (data.is_complete) {
        setIsComplete(true)
      } else if (data.agent_turn) {
        setTurns(prev => [...prev, {
          role: 'agent',
          content: data.agent_turn.content,
          turn_index: data.agent_turn.turn_index,
          intake_area: data.agent_turn.intake_area,
        }])
        if (data.missing_areas_remaining) {
          const covered = INTAKE_AREAS.filter(a => !data.missing_areas_remaining.includes(a))
          setCoveredAreas(covered)
        }
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send message')
      // Remove optimistic turn on error
      setTurns(prev => prev.slice(0, -1))
    } finally {
      setSending(false)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }

  const handleProcess = async () => {
    setProcessing(true)
    try {
      await processCase(caseId)
      navigate(`/cases/${caseId}/processing`)
    } catch (err) {
      setError(err.response?.data?.error || 'Processing failed')
      setProcessing(false)
    }
  }

  const requiredCoverage = REQUIRED_AREAS.filter(a => coveredAreas.includes(a)).length

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center">
          <Loader size={32} className="text-clinical-400 animate-spin mx-auto mb-3" />
          <p className="text-gray-400 text-sm">Starting interview...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto animate-fade-in">
      <div className="grid lg:grid-cols-[1fr_260px] gap-4">
        {/* Main conversation */}
        <div className="flex flex-col" style={{ height: 'calc(100vh - 180px)' }}>
          {/* Header */}
          <div className="card p-4 mb-4 flex items-center justify-between">
            <div>
              <h1 className="text-white font-semibold text-sm">Live Intake Interview</h1>
              <p className="text-gray-500 text-xs">AI-assisted. Not a clinical assessment.</p>
            </div>
            <div className="flex items-center gap-2">
              {sending && <Activity size={14} className="text-clinical-400 animate-pulse" />}
              <span className="text-xs text-gray-500">Turn {turns.length}</span>
            </div>
          </div>

          {/* Conversation */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
            {turns.map((turn, i) => (
              <div
                key={i}
                className={`flex ${turn.role === 'patient' ? 'justify-end' : 'justify-start'} animate-slide-up`}
              >
                <div className={`max-w-[80%] ${turn.role === 'agent' ? 'chat-bubble-agent' : 'chat-bubble-patient'} px-4 py-3`}>
                  {turn.role === 'agent' && (
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <Activity size={11} className="text-clinical-400" />
                      <span className="text-clinical-400 text-xs font-medium">Intake Agent</span>
                      {turn.intake_area && (
                        <span className="text-gray-600 text-xs">· {AREA_LABELS[turn.intake_area] || turn.intake_area}</span>
                      )}
                    </div>
                  )}
                  <p className="text-gray-200 text-sm leading-relaxed">{turn.content}</p>
                  <p className="text-gray-600 text-xs mt-1">Turn {turn.turn_index}</p>
                </div>
              </div>
            ))}

            {sending && (
              <div className="flex justify-start">
                <div className="chat-bubble-agent px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-clinical-400/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-2 h-2 bg-clinical-400/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-2 h-2 bg-clinical-400/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}

            {isComplete && (
              <div className="card p-5 border-emerald-500/20 bg-emerald-500/5 animate-slide-up">
                <div className="flex items-start gap-3">
                  <CheckCircle size={18} className="text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="text-emerald-300 font-semibold text-sm mb-1">Interview Complete</h3>
                    <p className="text-emerald-200/70 text-xs leading-relaxed mb-3">
                      Sufficient information has been collected. The multi-agent pipeline will now
                      structure, verify, and prepare a reviewer-ready brief.
                    </p>
                    <button
                      onClick={handleProcess}
                      disabled={processing}
                      className="btn-success flex items-center gap-2 text-sm"
                    >
                      {processing ? 'Starting processing...' : 'Process with Agents'}
                      {!processing && <ArrowRight size={14} />}
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          {!isComplete && (
            <>
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2 mb-2 flex items-center gap-2 text-red-400 text-sm">
                  <AlertCircle size={14} />
                  {error}
                </div>
              )}
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Type your response..."
                  className="input-field flex-1"
                  disabled={sending}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || sending}
                  className="btn-primary px-4 flex-shrink-0"
                >
                  <Send size={16} />
                </button>
              </div>
              <p className="text-xs text-gray-600 mt-2 text-center">
                This is a demo using synthetic data only. Do not enter real personal information.
              </p>
            </>
          )}
        </div>

        {/* Side panel: progress */}
        <div className="space-y-4">
          <div className="card p-4">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Coverage Progress
            </h2>
            <div className="mb-3">
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Required areas</span>
                <span>{requiredCoverage}/{REQUIRED_AREAS.length}</span>
              </div>
              <div className="confidence-bar">
                <div
                  className="confidence-fill bg-clinical-500"
                  style={{ width: `${(requiredCoverage / REQUIRED_AREAS.length) * 100}%` }}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              {INTAKE_AREAS.map(area => {
                const covered = coveredAreas.includes(area)
                const required = REQUIRED_AREAS.includes(area)
                return (
                  <div key={area} className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${covered ? 'bg-emerald-400' : required ? 'bg-gray-600' : 'bg-gray-700'}`} />
                    <span className={`text-xs ${covered ? 'text-emerald-400' : required ? 'text-gray-400' : 'text-gray-600'}`}>
                      {AREA_LABELS[area]}
                      {required && !covered && <span className="text-amber-500 ml-1">*</span>}
                    </span>
                  </div>
                )
              })}
            </div>
            <p className="text-xs text-gray-600 mt-2">* Required</p>
          </div>

          {/* Agent indicator */}
          <div className="card p-4">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Active Agent
            </h2>
            <div className="agent-activity-item">
              <div className="w-2 h-2 rounded-full bg-clinical-400 animate-pulse flex-shrink-0 mt-1.5" />
              <div>
                <div className="text-white text-xs font-medium">Intake Interviewer</div>
                <div className="text-gray-500 text-xs">Collecting structured information</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
