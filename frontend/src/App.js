import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import CreateCampaign from "./pages/CreateCampaign";
import LogoManager from "./pages/LogoManager";
import CampaignHistory from "./pages/CampaignHistory";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("come_token");
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <div className="App min-h-screen bg-[#050505]">
      <Toaster 
        position="top-right" 
        richColors 
        theme="dark"
        toastOptions={{
          style: {
            background: '#121212',
            border: '1px solid #333333',
            color: '#FFFFFF',
          },
        }}
      />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/create" element={<PrivateRoute><CreateCampaign /></PrivateRoute>} />
          <Route path="/logos" element={<PrivateRoute><LogoManager /></PrivateRoute>} />
          <Route path="/history" element={<PrivateRoute><CampaignHistory /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
