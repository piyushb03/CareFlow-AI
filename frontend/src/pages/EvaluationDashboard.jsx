import { useState, useEffect } from 'react'
import { getEvalResults, runEvaluation } from '../services/api'
import { BarChart2, Loader, Play, AlertTriangle } from 'lucide-react'

export default function EvaluationDashboard() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => { fetchResults() }, [])

  const fetchResults = async () => {
    try {
      const res = await getEvalResults()
      setResults(res.data)
    } catch {
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const handleRunEval = async (mode) => {
    setRunning(true)
    setError(null)
    try {
      await runEvaluation(mode)
      await fetchResults()
    } catch (err) {
      setError(err.response?.data?.error || 'Evaluation failed')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="animate-fade-in max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">Evaluation Dashboard</h1>
          <p className="text-gray-400 text-sm">
            Measured improvement of multi-agent pipeline vs single-prompt baseline.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleRunEval('baseline')}
            disabled={running}
            className="btn-secondary text-xs flex items-center gap-1"
          >
            {running ? <Loader size={12} className="animate-spin" /> : <Play size={12} />}
            Run Baseline
          </button>
          <button
            onClick={() => handleRunEval('agent')}
            disabled={running}
            className="btn-primary text-xs flex items-center gap-1"
          >
            {running ? <Loader size={12} className="animate-spin" /> : <Play size={12} />}
            Run Agent Eval
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4 text-red-400 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-24">
          <Loader size={24} className="text-clinical-400 animate-spin" />
        </div>
      ) : !results ? (
        <div className="card p-12 text-center">
          <BarChart2 size={40} className="text-gray-600 mx-auto mb-4" />
          <h2 className="text-white font-semibold mb-2">No Evaluation Results Yet</h2>
          <p className="text-gray-400 text-sm mb-4">
            Run the baseline and agent evaluations to see measured improvement.
          </p>
          <div className="flex gap-2 justify-center">
            <button onClick={() => handleRunEval('baseline')} className="btn-secondary text-sm">Run Baseline First</button>
            <button onClick={() => handleRunEval('agent')} className="btn-primary text-sm">Then Run Agent Eval</button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Summary */}
          {results.summary && (
            <div className="grid grid-cols-3 gap-3">
              <div className="card p-5 text-center">
                <div className="text-2xl font-bold text-gray-400">{results.summary.baseline_avg_score}</div>
                <div className="text-xs text-gray-500">Baseline Score</div>
                <div className="text-xs text-gray-600">Single-prompt</div>
              </div>
              <div className="card p-5 text-center border-clinical-500/20">
                <div className="text-2xl font-bold text-clinical-400">{results.summary.agent_avg_score}</div>
                <div className="text-xs text-gray-500">Agent Score</div>
                <div className="text-xs text-gray-600">Multi-agent pipeline</div>
              </div>
              <div className="card p-5 text-center border-emerald-500/20 bg-emerald-500/5">
                <div className="text-2xl font-bold text-emerald-400">+{results.summary.improvement}</div>
                <div className="text-xs text-gray-500">Improvement</div>
                <div className="text-xs text-emerald-600">{results.summary.improvement_pct}%</div>
              </div>
            </div>
          )}

          {/* Metrics table */}
          {results.metric_table && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-4">Metric Comparison</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="text-left text-gray-500 text-xs py-2 pr-4 font-medium">Metric</th>
                      <th className="text-left text-gray-500 text-xs py-2 pr-4 font-medium">Baseline</th>
                      <th className="text-left text-gray-500 text-xs py-2 pr-4 font-medium">Agent Pipeline</th>
                      <th className="text-left text-gray-500 text-xs py-2 font-medium">Change</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {results.metric_table.map((row, i) => (
                      <tr key={i}>
                        <td className="py-3 pr-4 text-gray-300">{row.metric}</td>
                        <td className="py-3 pr-4 text-gray-500">{row.baseline}</td>
                        <td className="py-3 pr-4 text-white">{row.agent}</td>
                        <td className={`py-3 font-medium ${row.change.startsWith('+') ? 'text-emerald-400' : 'text-gray-400'}`}>
                          {row.change}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Per-case */}
          {results.per_case_comparison && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-white mb-4">Per-Case Scores</h2>
              <div className="space-y-2">
                {results.per_case_comparison.map(c => (
                  <div key={c.case_id} className="flex items-center gap-3">
                    <span className="text-xs text-gray-500 w-16 flex-shrink-0">{c.case_id}</span>
                    <div className="flex-1 flex items-center gap-2">
                      <div className="confidence-bar flex-1">
                        <div className="confidence-fill bg-gray-700" style={{ width: `${c.baseline_score}%` }} />
                      </div>
                      <div className="confidence-bar flex-1">
                        <div className={`confidence-fill ${c.agent_score >= 70 ? 'bg-clinical-500' : 'bg-amber-500'}`} style={{ width: `${c.agent_score}%` }} />
                      </div>
                    </div>
                    <span className={`text-xs font-medium flex-shrink-0 ${c.delta > 0 ? 'text-emerald-400' : 'text-gray-500'}`}>
                      {c.delta > 0 ? '+' : ''}{c.delta}
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex gap-4 mt-3 text-xs text-gray-500">
                <span className="flex items-center gap-1"><span className="w-3 h-1 bg-gray-700 rounded block" /> Baseline</span>
                <span className="flex items-center gap-1"><span className="w-3 h-1 bg-clinical-500 rounded block" /> Agent</span>
              </div>
            </div>
          )}

          {/* Interpretation */}
          {results.interpretation && (
            <div className="disclaimer-bar flex items-start gap-2">
              <AlertTriangle size={13} className="flex-shrink-0 mt-0.5" />
              {results.interpretation}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
