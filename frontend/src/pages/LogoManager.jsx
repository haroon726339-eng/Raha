import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Plus,
  Trash2,
  Image,
  Shield,
  Trophy,
  Loader2,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COME_LOGO = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png";

export default function LogoManager() {
  const navigate = useNavigate();
  const [logos, setLogos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [addingLogo, setAddingLogo] = useState(false);
  const [activeTab, setActiveTab] = useState("team");

  const [newLogo, setNewLogo] = useState({
    name: "",
    short_name: "",
    logo_url: "",
    category: "team",
  });

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("come_token")}`,
  });

  useEffect(() => {
    fetchLogos();
  }, []);

  const fetchLogos = async () => {
    try {
      const response = await axios.get(`${API}/logos`, { headers: getAuthHeaders() });
      setLogos(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        navigate("/login");
      }
      toast.error("Failed to fetch logos");
    } finally {
      setLoading(false);
    }
  };

  const addLogo = async () => {
    if (!newLogo.name || !newLogo.short_name || !newLogo.logo_url) {
      toast.error("Please fill all fields");
      return;
    }

    setAddingLogo(true);
    try {
      await axios.post(`${API}/logos`, newLogo, { headers: getAuthHeaders() });
      toast.success("Logo added successfully");
      setNewLogo({ name: "", short_name: "", logo_url: "", category: "team" });
      setShowAddForm(false);
      fetchLogos();
    } catch (error) {
      toast.error("Failed to add logo");
    } finally {
      setAddingLogo(false);
    }
  };

  const deleteLogo = async (logoId) => {
    if (!window.confirm("Are you sure you want to delete this logo?")) return;

    try {
      await axios.delete(`${API}/logos/${logoId}`, { headers: getAuthHeaders() });
      toast.success("Logo deleted");
      fetchLogos();
    } catch (error) {
      toast.error("Failed to delete logo");
    }
  };

  const seedLogos = async () => {
    try {
      const response = await axios.post(`${API}/seed-logos`, {}, { headers: getAuthHeaders() });
      toast.success(response.data.message);
      fetchLogos();
    } catch (error) {
      toast.error("Failed to seed logos");
    }
  };

  const teamLogos = logos.filter((l) => l.category === "team");
  const tournamentLogos = logos.filter((l) => l.category === "tournament");

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Header */}
      <header className="bg-[#121212] border-b border-[#333333] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="text-[#A1A1AA] hover:text-white">
              <ArrowLeft size={24} />
            </Link>
            <img src={COME_LOGO} alt="COME" className="w-10 h-10 object-contain" />
            <h1 className="font-['Teko'] text-xl text-white uppercase">Logo Manager</h1>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary flex items-center gap-2 text-sm py-2 px-4"
              data-testid="add-logo-button"
            >
              <Plus size={16} />
              Add Logo
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab("team")}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === "team"
                ? "bg-[#00FF88]/10 text-[#00FF88] border border-[#00FF88]"
                : "bg-[#121212] text-[#A1A1AA] border border-[#333333] hover:border-[#00FF88]"
            }`}
            data-testid="team-tab"
          >
            <Shield size={20} />
            <span className="font-['Teko'] text-lg uppercase">Teams ({teamLogos.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("tournament")}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg transition-all ${
              activeTab === "tournament"
                ? "bg-[#FFD700]/10 text-[#FFD700] border border-[#FFD700]"
                : "bg-[#121212] text-[#A1A1AA] border border-[#333333] hover:border-[#FFD700]"
            }`}
            data-testid="tournament-tab"
          >
            <Trophy size={20} />
            <span className="font-['Teko'] text-lg uppercase">Tournaments ({tournamentLogos.length})</span>
          </button>
        </div>

        {/* Seed Button */}
        {logos.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8"
          >
            <button
              onClick={seedLogos}
              className="btn-outline w-full flex items-center justify-center gap-2"
              data-testid="seed-logos-button"
            >
              <Image size={20} />
              Load Default Cricket Team & Tournament Logos
            </button>
          </motion.div>
        )}

        {/* Logos Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="logo-grid"
        >
          {(activeTab === "team" ? teamLogos : tournamentLogos).map((logo, index) => (
            <motion.div
              key={logo.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              className="logo-card relative group"
              data-testid={`logo-${logo.short_name}`}
            >
              <button
                onClick={() => deleteLogo(logo.id)}
                className="absolute top-2 right-2 p-2 bg-[#FF4444]/20 rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-[#FF4444]/40"
                data-testid={`delete-${logo.short_name}`}
              >
                <Trash2 size={14} className="text-[#FF4444]" />
              </button>
              <img
                src={logo.logo_url}
                alt={logo.name}
                className="w-16 h-16 mx-auto object-contain"
                onError={(e) => { e.target.src = 'https://via.placeholder.com/64?text=' + logo.short_name; }}
              />
              <p className="text-white font-medium mt-3">{logo.name}</p>
              <p className="text-[#A1A1AA] text-sm">{logo.short_name}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Empty State */}
        {(activeTab === "team" ? teamLogos : tournamentLogos).length === 0 && (
          <div className="text-center py-16">
            <Image size={64} className="mx-auto text-[#333333] mb-4" />
            <p className="text-[#A1A1AA] mb-4">
              No {activeTab} logos yet
            </p>
            <button
              onClick={() => {
                setNewLogo({ ...newLogo, category: activeTab });
                setShowAddForm(true);
              }}
              className="text-[#00FF88] hover:underline"
            >
              Add your first {activeTab} logo
            </button>
          </div>
        )}

        {/* Add Logo Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-[#121212] border border-[#333333] rounded-2xl p-6 w-full max-w-md"
            >
              <h2 className="font-['Teko'] text-2xl text-white uppercase mb-6">Add New Logo</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Name</label>
                  <input
                    type="text"
                    value={newLogo.name}
                    onChange={(e) => setNewLogo({ ...newLogo, name: e.target.value })}
                    className="form-input w-full"
                    placeholder="India"
                    data-testid="new-logo-name"
                  />
                </div>

                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Short Name</label>
                  <input
                    type="text"
                    value={newLogo.short_name}
                    onChange={(e) => setNewLogo({ ...newLogo, short_name: e.target.value })}
                    className="form-input w-full"
                    placeholder="IND"
                    data-testid="new-logo-short-name"
                  />
                </div>

                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Logo URL</label>
                  <input
                    type="text"
                    value={newLogo.logo_url}
                    onChange={(e) => setNewLogo({ ...newLogo, logo_url: e.target.value })}
                    className="form-input w-full"
                    placeholder="https://..."
                    data-testid="new-logo-url"
                  />
                </div>

                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Category</label>
                  <select
                    value={newLogo.category}
                    onChange={(e) => setNewLogo({ ...newLogo, category: e.target.value })}
                    className="form-input w-full"
                    data-testid="new-logo-category"
                  >
                    <option value="team">Team</option>
                    <option value="tournament">Tournament</option>
                  </select>
                </div>

                {newLogo.logo_url && (
                  <div className="text-center p-4 bg-[#1E1E1E] rounded-lg">
                    <p className="text-[#A1A1AA] text-sm mb-2">Preview</p>
                    <img
                      src={newLogo.logo_url}
                      alt="Preview"
                      className="w-16 h-16 mx-auto object-contain"
                      onError={(e) => { e.target.src = 'https://via.placeholder.com/64?text=Error'; }}
                    />
                  </div>
                )}
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => setShowAddForm(false)}
                  className="btn-outline flex-1"
                  data-testid="cancel-add-logo"
                >
                  Cancel
                </button>
                <button
                  onClick={addLogo}
                  disabled={addingLogo}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                  data-testid="confirm-add-logo"
                >
                  {addingLogo ? (
                    <Loader2 className="animate-spin" size={20} />
                  ) : (
                    <Plus size={20} />
                  )}
                  {addingLogo ? "Adding..." : "Add Logo"}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}
