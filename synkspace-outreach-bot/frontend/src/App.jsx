import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Home from './pages/Home'
import UploadCSV from './components/UploadCSV'
import Campaigns from './pages/Campaigns'

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<UploadCSV />} />
          <Route path="/campaigns" element={<Campaigns />} />
        </Routes>
      </main>
    </div>
  )
}
