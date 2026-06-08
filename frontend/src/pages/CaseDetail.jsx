import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCase, getConversation, approveCase, rejectCase, reviewCase } from '../services/api'
import {
  AlertTriangle, CheckCircle, Eye, FileText, Search,
  ThumbsUp, ThumbsDown, ArrowRight, Shield, Clock, Loader
} from 'lucide-react'

const PriorityBar = ({ priority }) => {
  const colors = { HIGH: 'bg-red-500', MEDIUM: 'bg-amber-500', STANDARD: 'bg-emerald-500', URGENT: 'bg-red-600' }
  const labels = { HIGH: 'High Priority', MEDIUM: 'Medium Priority', STANDARD: 'Standard Review', URGENT: 'Urgent' }
  return (
    <div className={`rounded-2xl p-4 border ${
      priority === 'HIGH' || priority === 'URGENT' ? 'border-red-500/20 bg-red-500/5' :
      priority === 'MEDIUM' ? 'border-amber-500/20 bg-amber-500/5' : 'border-emerald-500/20 bg-emerald-500/5'
    }`}>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${colors[priority] || 'bg-gray-500'}`} />
        <span className="text-sm font-semibold text-white">{labels[priority] || priority}</span>
      </div>
    </div>
  )
}

const SignalBadge = ({ status }) => {
  const map = {
    present: 'bg-red-500/15 text-red-400 border-red-500/20',
    absent: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/20',
    unclear: 'bg-amber-500/15 text-amber-400 border-amber-500/20',
    not_assessed: 'bg-gray-500/15 text-gray-400 border-gray-500/20',
  }
  return <span className={`badge border ${map[status] || map.not_assessed}`}>{status}</span>
}

export default function CaseDetail() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [conversation, setConversation] = useState([])
  const [loading, setLoading] = useState(true)
  const [reviewerNotes, setReviewerNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [actionDone, setActionDone] = useState(null)

  useEffect(() => {
    Promise.all([getCase(caseId), getConversation(caseId)]).then(([cRes, convRes]) => {
      setCaseData(cRes.data)
      setConversation(convRes.data.turns || [])
      setReviewerNotes(cRes.data.reviewer_notes || '')
    }).finally(() => setLoading(false))
  }, [caseId])

  const handleApprove = async () => {
    setSubmitting(true)
    await approveCase(caseId, { notes: reviewerNotes, reviewer_id: 'reviewer-demo' })
    setActionDone('approved')
    setSubmitting(false)
  }

  const handleReject = async () => {
    setSubmitting(true)
    await rejectCase(caseId, { reason: reviewerNotes || 'Insufficient quality', reviewer_id: 'reviewer-demo' })
    setActionDone('rejected')
    setSubmitting(false)
  }

  const handleSaveNotes = async () => {
    setSubmitting(true)
    await reviewCase(caseId, { notes: reviewerNotes, reviewer_id: 'reviewer-demo' })
    setSubmitting(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader size={28} className="text-clinical-400 animate-spin" />
      </div>
    )
  }

  if (!caseData) return <div className="text-red-400">Case not found</div>

  const brief = caseData.reviewer_brief || {}
  const safetySignals = brief.safety_signals?.all_signals || []
  const priorities = brief.reviewer_attention_priorities || []
  const verificationStatus = caseData.verification_status || 'pending'

  return (
    <div className="animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">
            {caseData.case_ref || caseData.id.slice(0, 12)}
          </h1>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="badge-neutral">{caseData.status}</span>
            <span className={verificationStatus === 'passed' ? 'badge-low' : 'badge-medium'}>
              {verificationStatus === 'passed' ? '✓ Verified' : '⚠ ' + verificationStatus}
            </span>
            <span className="text-gray-500 text-xs">
              <Clock size={11} className="inline mr-1" />
              {new Date(caseData.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        <div className="flex gap-2 flex-wrap">
          <button onClick={() => navigate(`/cases/${caseId}/evidence`)} className="btn-secondary text-xs flex items-center gap-1">
            <Search size={12} /> Evidence
          </button>
          <button onClick={() => navigate(`/cases/${caseId}/verification`)} className="btn-secondary text-xs flex items-center gap-1">
            <Eye size={12} /> Verification
          </button>
        </div>
      </div>

      {/* Human Review Gate */}
      <div className="review-gate p-5 mb-6">
        <div className="flex items-start gap-3">
          <Shield size={18} className="text-clinical-400 flex-shrink-0 mt-0.5" />
          <div>
            <h2 className="text-clinical-300 font-semibold mb-1">READY FOR HUMAN REVIEW</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              This intake brief has been prepared by the AI pipeline and awaits review by a qualified mental health professional.
              CareFlow AI does not make clinical decisions. The reviewer must independently assess all information,
              safety signals, and missing data before any clinical action.
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          {/* Reviewer priorities */}
          {priorities.length > 0 && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <AlertTriangle size={15} className="text-amber-400" />
                Reviewer Attention Priorities
              </h2>
              <div className="space-y-2">
                {priorities.map((p, i) => (
                  <div key={i} className={`rounded-xl p-3 border ${
                    p.priority === 'URGENT' ? 'border-red-500/20 bg-red-500/5' :
                    p.priority === 'HIGH' ? 'border-red-500/15 bg-red-500/3' :
                    p.priority === 'MEDIUM' ? 'border-amber-500/20 bg-amber-500/5' : 'border-white/5 bg-white/2'
                  }`}>
                    <div className="flex items-start gap-2">
                      <span className={`text-xs font-bold ${
                        p.priority === 'URGENT' || p.priority === 'HIGH' ? 'text-red-400' :
                        p.priority === 'MEDIUM' ? 'text-amber-400' : 'text-emerald-400'
                      }`}>{p.priority}</span>
                      <span className="text-xs text-gray-400 font-medium">{p.area}:</span>
                      <span className="text-xs text-gray-300 flex-1">{p.description}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Presenting concerns */}
          {brief.presenting_concerns && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-3">Presenting Concerns</h2>
              <p className="text-gray-300 text-sm leading-relaxed">{brief.presenting_concerns}</p>
            </div>
          )}

          {/* Safety signals */}
          {safetySignals.length > 0 && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
                <Shield size={15} className="text-red-400" />
                Safety-Relevant Signals
              </h2>
              <p className="text-xs text-gray-500 mb-3">
                For qualified reviewer attention only — not diagnoses or clinical conclusions.
              </p>
              <div className="space-y-2">
                {safetySignals.filter(s => s.status !== 'not_assessed').map((sig, i) => (
                  <div key={i} className="rounded-xl p-3 bg-white/2 border border-white/5">
                    <div className="flex items-center gap-2 mb-1.5">
                      <SignalBadge status={sig.status} />
                      <span className="text-sm font-medium text-white capitalize">
                        {sig.signal.replace(/_/g, ' ')}
                      </span>
                      {sig.requires_reviewer_attention && (
                        <AlertTriangle size={12} className="text-amber-400" />
                      )}
                    </div>
                    {sig.evidence && sig.evidence !== 'not established' && (
                      <div className="evidence-block text-xs mt-1.5">
                        "{sig.evidence}"
                        {sig.source_turns?.length > 0 && (
                          <span className="text-gray-500 not-italic ml-2">
                            — Turn {sig.source_turns.join(', ')}
                          </span>
                        )}
                      </div>
                    )}
                    {sig.confidence !== undefined && (
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-xs text-gray-600">Confidence:</span>
                        <div className="confidence-bar flex-1 max-w-24">
                          <div
                            className={`confidence-fill ${sig.confidence > 0.7 ? 'bg-emerald-500' : sig.confidence > 0.5 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${(sig.confidence || 0) * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">{((sig.confidence || 0) * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Missing information */}
          {brief.missing_information?.length > 0 && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-3">Missing Information</h2>
              <ul className="space-y-1">
                {brief.missing_information.map((item, i) => (
                  <li key={i} className="text-sm text-amber-300/80 flex items-start gap-2">
                    <span className="text-amber-500 mt-0.5">?</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Contradictions */}
          {brief.contradictions?.length > 0 && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <AlertTriangle size={14} className="text-red-400" />
                Contradictions Detected
              </h2>
              <div className="space-y-3">
                {brief.contradictions.map((c, i) => (
                  <div key={i} className="rounded-xl p-3 bg-red-500/5 border border-red-500/15">
                    <div className="text-xs font-medium text-red-300 mb-1">{c.field}</div>
                    <p className="text-xs text-gray-400 mb-2">{c.description}</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="evidence-block text-xs">"{c.evidence_a}" <span className="text-gray-600">(Turn {c.turn_a})</span></div>
                      <div className="evidence-block text-xs">"{c.evidence_b}" <span className="text-gray-600">(Turn {c.turn_b})</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Conversation */}
          <div className="card p-5">
            <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <FileText size={15} className="text-gray-400" />
              Original Conversation
            </h2>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {conversation.map((turn) => (
                <div key={turn.turn_index} className="flex gap-3">
                  <span className="text-gray-600 text-xs font-mono flex-shrink-0 w-14">T{turn.turn_index} {turn.role === 'agent' ? 'INT' : 'PAT'}</span>
                  <p className="text-sm text-gray-300 leading-relaxed">{turn.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Reviewer actions panel */}
        <div className="space-y-4">
          {/* Status */}
          <div className="card p-4">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Review Status</h2>
            <div className={`rounded-xl p-3 text-center border ${
              actionDone === 'approved' ? 'border-emerald-500/20 bg-emerald-500/5 text-emerald-300' :
              actionDone === 'rejected' ? 'border-red-500/20 bg-red-500/5 text-red-300' :
              'border-amber-500/20 bg-amber-500/5 text-amber-300'
            }`}>
              <span className="text-sm font-medium">
                {actionDone === 'approved' ? '✓ Approved by Reviewer' :
                 actionDone === 'rejected' ? '✗ Rejected by Reviewer' :
                 'Awaiting Qualified Reviewer'}
              </span>
            </div>
          </div>

          {/* Notes */}
          <div className="card p-4">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Reviewer Notes</h2>
            <textarea
              value={reviewerNotes}
              onChange={e => setReviewerNotes(e.target.value)}
              placeholder="Add reviewer observations, corrections, or clinical notes..."
              className="input-field text-sm resize-none"
              rows={4}
            />
            <button onClick={handleSaveNotes} disabled={submitting} className="btn-secondary text-xs mt-2 w-full">
              Save Notes
            </button>
          </div>

          {/* Actions */}
          {!actionDone && (
            <div className="card p-4 space-y-2">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Reviewer Actions</h2>
              <button
                onClick={handleApprove}
                disabled={submitting}
                className="btn-success w-full flex items-center justify-center gap-2 text-sm"
              >
                <ThumbsUp size={14} />
                Approve Summary
              </button>
              <button
                onClick={handleReject}
                disabled={submitting}
                className="btn-danger w-full flex items-center justify-center gap-2 text-sm"
              >
                <ThumbsDown size={14} />
                Reject — Needs Rework
              </button>
              <p className="text-xs text-gray-600 text-center">
                Approval does not constitute a clinical decision.
              </p>
            </div>
          )}

          {/* Uncertainty */}
          {brief.uncertainty && (
            <div className="card p-4">
              <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Uncertainty</h2>
              <p className="text-xs text-gray-400 leading-relaxed">{brief.uncertainty.summary}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
