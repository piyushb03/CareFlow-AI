import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { getEvidence, getConversation } from '../services/api'
import { Search, Info, Loader } from 'lucide-react'

const statusColor = { explicit: 'field-explicit', inferred: 'field-inferred', unknown: 'field-unknown', contradictory: 'field-contradictory' }
const statusLabel = { explicit: 'Explicitly stated', inferred: 'Inferred', unknown: 'Not established', contradictory: 'Contradictory' }

export default function EvidenceExplorer() {
  const { caseId } = useParams()
  const [fields, setFields] = useState([])
  const [signals, setSignals] = useState([])
  const [conversation, setConversation] = useState([])
  const [selected, setSelected] = useState(null)
  const [searchQ, setSearchQ] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getEvidence(caseId), getConversation(caseId)]).then(([evRes, convRes]) => {
      setFields(evRes.data.extracted_fields || [])
      setSignals(evRes.data.safety_signals || [])
      setConversation(convRes.data.turns || [])
    }).finally(() => setLoading(false))
  }, [caseId])

  const allItems = [
    ...fields.map(f => ({ ...f, _type: 'field', _label: f.field_name })),
    ...signals.map(s => ({ ...s, _type: 'signal', _label: s.signal })),
  ]

  const filtered = allItems.filter(item => {
    if (!searchQ) return true
    return item._label.toLowerCase().includes(searchQ.toLowerCase()) ||
           (item.value || '').toLowerCase().includes(searchQ.toLowerCase()) ||
           (item.evidence || '').toLowerCase().includes(searchQ.toLowerCase())
  })

  const getConversationTurn = (turnIdx) => conversation.find(t => t.turn_index === turnIdx)

  if (loading) return (
    <div className="flex items-center justify-center py-24">
      <Loader size={24} className="text-clinical-400 animate-spin" />
    </div>
  )

  return (
    <div className="animate-fade-in max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-white mb-1">Evidence Explorer</h1>
        <p className="text-gray-400 text-sm">
          Click any field to inspect its evidence chain, source turn, and confidence.
        </p>
      </div>

      <div className="mb-4">
        <div className="relative">
          <Search size={15} className="absolute left-3 top-3.5 text-gray-500" />
          <input
            value={searchQ}
            onChange={e => setSearchQ(e.target.value)}
            placeholder="Search fields, values, or evidence..."
            className="input-field pl-9"
          />
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* Field list */}
        <div className="card divide-y divide-white/5 max-h-[600px] overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="p-8 text-center text-gray-500 text-sm">No fields found</div>
          ) : filtered.map((item, i) => (
            <button
              key={i}
              onClick={() => setSelected(item)}
              className={`w-full text-left p-3 hover:bg-white/3 transition-all ${selected?._label === item._label ? 'bg-clinical-500/10' : ''}`}
            >
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-sm font-medium text-white capitalize">
                  {item._label.replace(/_/g, ' ')}
                </span>
                <span className={`text-xs ${statusColor[item.status] || 'text-gray-500'}`}>
                  {item.status}
                </span>
              </div>
              <div className="text-xs text-gray-500 truncate">
                {item.value || item.evidence || 'No value'}
              </div>
              {item._type === 'signal' && (
                <span className={`badge mt-1 ${
                  item.status === 'present' ? 'bg-red-500/15 text-red-400' :
                  item.status === 'absent' ? 'bg-emerald-500/15 text-emerald-400' :
                  'bg-gray-500/15 text-gray-400'
                }`}>{item.status}</span>
              )}
            </button>
          ))}
        </div>

        {/* Detail panel */}
        <div className="card p-5">
          {!selected ? (
            <div className="h-full flex items-center justify-center text-gray-600 text-sm">
              <div className="text-center">
                <Info size={32} className="mx-auto mb-3 opacity-40" />
                <p>Select a field to inspect evidence</p>
              </div>
            </div>
          ) : (
            <div className="animate-fade-in space-y-4">
              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Field</div>
                <h2 className="text-lg font-semibold text-white capitalize">
                  {selected._label.replace(/_/g, ' ')}
                </h2>
                {selected.category && (
                  <span className="text-xs text-gray-500">{selected.category}</span>
                )}
              </div>

              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Value</div>
                <p className="text-sm text-white">{selected.value || selected.status || '—'}</p>
              </div>

              <div>
                <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Status</div>
                <span className={`text-sm font-medium ${statusColor[selected.status]}`}>
                  {statusLabel[selected.status] || selected.status}
                </span>
              </div>

              {selected.evidence && selected.evidence !== 'not established' && (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Evidence</div>
                  <div className="evidence-block">"{selected.evidence}"</div>
                </div>
              )}

              {selected.source_turns?.length > 0 && (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Source Turns</div>
                  <div className="space-y-2">
                    {selected.source_turns.map(turnIdx => {
                      const turn = getConversationTurn(turnIdx)
                      return turn ? (
                        <div key={turnIdx} className="rounded-xl p-3 bg-white/3 border border-white/5">
                          <div className="text-xs text-gray-500 mb-1">
                            Turn {turnIdx} — {turn.role.toUpperCase()}
                          </div>
                          <p className="text-xs text-gray-300">{turn.content}</p>
                        </div>
                      ) : (
                        <div key={turnIdx} className="text-xs text-gray-600">Turn {turnIdx}</div>
                      )
                    })}
                  </div>
                </div>
              )}

              {selected.confidence !== undefined && (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-2">Confidence</div>
                  <div className="flex items-center gap-3">
                    <div className="confidence-bar flex-1">
                      <div
                        className={`confidence-fill ${selected.confidence > 0.7 ? 'bg-emerald-500' : selected.confidence > 0.5 ? 'bg-amber-500' : 'bg-red-500'}`}
                        style={{ width: `${(selected.confidence || 0) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-white font-mono">
                      {((selected.confidence || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}

              {selected.uncertainty_note || selected.uncertainty ? (
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Uncertainty</div>
                  <p className="text-xs text-amber-300/80 italic">
                    {selected.uncertainty_note || selected.uncertainty}
                  </p>
                </div>
              ) : null}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
