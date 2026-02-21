import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import ProjectDetailsPage from './pages/ProjectDetailsPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/project/:taskId" element={<ProjectDetailsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
