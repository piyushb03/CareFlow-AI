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
