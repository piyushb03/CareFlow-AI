import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { listCases } from '../services/api'
import { ArrowRight, Clock, AlertTriangle, CheckCircle, Eye, Loader } from 'lucide-react'

const StatusBadge = ({ status }) => {
  const map = {
    intake: { cls: 'badge-info', label: 'Intake' },
    processing: { cls: 'badge-info', label: 'Processing' },
    ready_for_review: { cls: 'badge-medium', label: 'Needs Review' },
    reviewed: { cls: 'badge-low', label: 'Reviewed' },
    error: { cls: 'badge-high', label: 'Error' },
  }
  const { cls, label } = map[status] || { cls: 'badge-neutral', label: status }
  return <span className={cls}>{label}</span>
}

const PriorityBadge = ({ verificationStatus }) => {
  if (verificationStatus === 'requires_human_review') return <span className="badge-high">⚠ Review Required</span>
  if (verificationStatus === 'passed') return <span className="badge-low">✓ Verified</span>
  return <span className="badge-neutral">Pending</span>
}

export default function ReviewerDashboard() {
  const navigate = useNavigate()
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => { fetchCases() }, [])

  const fetchCases = async () => {
    try {
      const res = await listCases({ per_page: 50 })
      setCases(res.data.cases || [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const filtered = filter === 'all' ? cases : cases.filter(c => c.status === filter || c.reviewer_status === filter)

  const stats = {
    total: cases.length,
    needs_review: cases.filter(c => c.status === 'ready_for_review').length,
    reviewed: cases.filter(c => c.status === 'reviewed').length,
    high_priority: cases.filter(c => c.verification_status === 'requires_human_review').length,
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Reviewer Dashboard</h1>
          <p className="text-gray-400 text-sm">
            All outputs require review by a qualified mental health professional.
          </p>
        </div>
        <button onClick={() => navigate('/intake/new')} className="btn-primary text-sm">
          New Intake
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[
          { label: 'Total Cases', value: stats.total, color: 'text-white' },
          { label: 'Needs Review', value: stats.needs_review, color: 'text-amber-400' },
          { label: 'Reviewed', value: stats.reviewed, color: 'text-emerald-400' },
          { label: 'High Priority', value: stats.high_priority, color: 'text-red-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-4 text-center">
            <div className={`text-2xl font-bold ${color} mb-0.5`}>{value}</div>
            <div className="text-gray-500 text-xs">{label}</div>
          </div>
        ))}
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4 flex-wrap">
        {['all', 'ready_for_review', 'reviewed', 'intake'].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === f ? 'bg-clinical-600 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {f === 'all' ? 'All' : f === 'ready_for_review' ? 'Needs Review' : f === 'reviewed' ? 'Reviewed' : 'In Intake'}
          </button>
        ))}
      </div>

      {/* Cases table */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader size={24} className="text-clinical-400 animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-gray-500 mb-4">No cases found</p>
          <button onClick={() => navigate('/intake/new')} className="btn-primary text-sm">
            Start First Intake
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {filtered.map(c => (
            <div
              key={c.id}
              className="card-hover p-4 cursor-pointer"
              onClick={() => navigate(`/cases/${c.id}`)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-white font-medium text-sm truncate">
                        {c.case_ref || c.id.slice(0, 8)}
                      </span>
                      <StatusBadge status={c.status} />
                      <PriorityBadge verificationStatus={c.verification_status} />
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock size={11} />
                        {new Date(c.created_at).toLocaleDateString()}
                      </span>
                      <span>Reviewer: {c.reviewer_status || 'awaiting'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {c.status === 'ready_for_review' && (
                    <button
                      onClick={e => { e.stopPropagation(); navigate(`/cases/${c.id}`) }}
                      className="btn-secondary text-xs flex items-center gap-1"
                    >
                      <Eye size={12} /> Review
                    </button>
                  )}
                  <ArrowRight size={15} className="text-gray-600" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <div className="disclaimer-bar mt-6 flex items-start gap-2">
        <AlertTriangle size={13} className="flex-shrink-0 mt-0.5" />
        <span>
          All cases displayed are synthetic demos. CareFlow AI outputs are intake preparation tools only —
          not clinical assessments. Every output requires qualified professional review before any clinical action.
        </span>
      </div>
    </div>
  )
}
