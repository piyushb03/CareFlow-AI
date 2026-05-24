import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import NewIntake from './pages/NewIntake'
import LiveIntake from './pages/LiveIntake'
import AgentActivity from './pages/AgentActivity'
import ReviewerDashboard from './pages/ReviewerDashboard'
import CaseDetail from './pages/CaseDetail'
import EvidenceExplorer from './pages/EvidenceExplorer'
import VerificationResults from './pages/VerificationResults'
import EvaluationDashboard from './pages/EvaluationDashboard'
import About from './pages/About'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Landing />} />
          <Route path="intake/new" element={<NewIntake />} />
          <Route path="intake/:caseId/conversation" element={<LiveIntake />} />
          <Route path="cases/:caseId/processing" element={<AgentActivity />} />
          <Route path="dashboard" element={<ReviewerDashboard />} />
          <Route path="cases/:caseId" element={<CaseDetail />} />
          <Route path="cases/:caseId/evidence" element={<EvidenceExplorer />} />
          <Route path="cases/:caseId/verification" element={<VerificationResults />} />
          <Route path="evaluation" element={<EvaluationDashboard />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
