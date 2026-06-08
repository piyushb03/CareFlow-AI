import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getVerification } from '../services/api'
import { CheckCircle, AlertTriangle, XCircle, Loader } from 'lucide-react'

const SeverityIcon = ({ severity }) => {
  if (severity === 'high') return <XCircle size={14} className="text-red-400" />
  if (severity === 'medium') return <AlertTriangle size={14} className="text-amber-400" />
  return <AlertTriangle size={14} className="text-gray-400" />
}

export default function VerificationResults() {
  const { caseId } = useParams()
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getVerification(caseId).then(res => setIssues(res.data.issues || [])).finally(() => setLoading(false))
  }, [caseId])

  const high = issues.filter(i => i.severity === 'high')
  const medium = issues.filter(i => i.severity === 'medium')
  const low = issues.filter(i => i.severity === 'low')

  if (loading) return <div className="flex justify-center py-24"><Loader size={24} className="text-clinical-400 animate-spin" /></div>

  return (
    <div className="animate-fade-in max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white mb-1">Verification Results</h1>
        <p className="text-gray-400 text-sm">
          Issues found by the Verification Agent before human handoff.
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="card p-4 text-center border-red-500/10">
          <div className="text-2xl font-bold text-red-400">{high.length}</div>
          <div className="text-xs text-gray-500">High Severity</div>
        </div>
        <div className="card p-4 text-center border-amber-500/10">
          <div className="text-2xl font-bold text-amber-400">{medium.length}</div>
          <div className="text-xs text-gray-500">Medium Severity</div>
        </div>
        <div className="card p-4 text-center">
          <div className="text-2xl font-bold text-gray-400">{low.length}</div>
          <div className="text-xs text-gray-500">Low Severity</div>
        </div>
      </div>

      {issues.length === 0 ? (
        <div className="card p-8 text-center border-emerald-500/20 bg-emerald-500/5">
          <CheckCircle size={32} className="text-emerald-400 mx-auto mb-3" />
          <h2 className="text-emerald-300 font-semibold">Verification Passed</h2>
          <p className="text-gray-400 text-sm mt-1">No issues were detected by the Verification Agent.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {issues.map((issue, i) => (
            <div key={i} className={`card p-4 border ${
              issue.severity === 'high' ? 'border-red-500/20 bg-red-500/5' :
              issue.severity === 'medium' ? 'border-amber-500/20 bg-amber-500/5' : 'border-white/5'
            }`}>
              <div className="flex items-start gap-3">
                <SeverityIcon severity={issue.severity} />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-white capitalize">
                      {issue.issue_type?.replace(/_/g, ' ')}
                    </span>
                    <span className={`badge ${issue.severity === 'high' ? 'badge-high' : issue.severity === 'medium' ? 'badge-medium' : 'badge-neutral'}`}>
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-2">{issue.description}</p>
                  {issue.evidence && (
                    <div className="evidence-block text-xs mb-2">"{issue.evidence}"</div>
                  )}
                  {issue.recommended_fix && (
                    <p className="text-xs text-clinical-400">
                      → Fix: {issue.recommended_fix}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
