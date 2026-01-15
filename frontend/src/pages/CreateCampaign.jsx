import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Send,
  Eye,
  User,
  Mail,
  Trophy,
  Calendar,
  Loader2,
  CheckCircle,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COME_LOGO = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png";

export default function CreateCampaign() {
  const navigate = useNavigate();
  const [logos, setLogos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [previewHtml, setPreviewHtml] = useState("");
  const [createdCampaignId, setCreatedCampaignId] = useState(null);

  const [formData, setFormData] = useState({
    winner_name: "",
    winner_email: "",
    winning_amount: "",
    contests_won: 1,
    team1_name: "",
    team1_logo: "",
    team2_name: "",
    team2_logo: "",
    match_date: new Date().toLocaleDateString('en-GB'),
    prize_pool: "",
    spots: "",
    entry_fee: "0",
    rank: 1,
    tournament_name: "",
    tournament_logo: "",
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
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const selectTeamLogo = (field, logo) => {
    handleChange(field === 'team1' ? 'team1_name' : 'team2_name', logo.name);
    handleChange(field === 'team1' ? 'team1_logo' : 'team2_logo', logo.logo_url);
  };

  const teamLogos = logos.filter((l) => l.category === "team");
  const tournamentLogos = logos.filter((l) => l.category === "tournament");

  const isFormValid = () => {
    return (
      formData.winner_name &&
      formData.winner_email &&
      formData.winning_amount &&
      formData.team1_name &&
      formData.team1_logo &&
      formData.team2_name &&
      formData.team2_logo &&
      formData.prize_pool &&
      formData.spots
    );
  };

  const createCampaign = async () => {
    if (!isFormValid()) {
      toast.error("Please fill all required fields");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/campaigns`, formData, {
        headers: getAuthHeaders(),
      });
      setCreatedCampaignId(response.data.id);
      toast.success("Campaign created!");
      
      // Get preview
      const previewRes = await axios.post(
        `${API}/campaigns/${response.data.id}/preview`,
        {},
        { headers: getAuthHeaders() }
      );
      setPreviewHtml(previewRes.data.html);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create campaign");
    } finally {
      setLoading(false);
    }
  };

  const sendEmail = async () => {
    if (!createdCampaignId) return;

    setSending(true);
    try {
      const response = await axios.post(
        `${API}/campaigns/${createdCampaignId}/send`,
        {},
        { headers: getAuthHeaders() }
      );
      toast.success(`Email sent to ${formData.winner_email}!`);
      navigate("/history");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send email");
    } finally {
      setSending(false);
    }
  };

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
            <h1 className="font-['Teko'] text-xl text-white uppercase">Create Campaign</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Form Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            {/* Winner Details */}
            <div className="dashboard-card">
              <h2 className="font-['Teko'] text-xl text-white uppercase mb-4 flex items-center gap-2">
                <User size={20} className="text-[#00FF88]" />
                Winner Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Winner Name *</label>
                  <input
                    type="text"
                    value={formData.winner_name}
                    onChange={(e) => handleChange("winner_name", e.target.value)}
                    className="form-input w-full"
                    placeholder="Aryan"
                    data-testid="winner-name-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Winner Email *</label>
                  <input
                    type="email"
                    value={formData.winner_email}
                    onChange={(e) => handleChange("winner_email", e.target.value)}
                    className="form-input w-full"
                    placeholder="winner@email.com"
                    data-testid="winner-email-input"
                  />
                </div>
              </div>
            </div>

            {/* Winning Details */}
            <div className="dashboard-card">
              <h2 className="font-['Teko'] text-xl text-white uppercase mb-4 flex items-center gap-2">
                <Trophy size={20} className="text-[#FFD700]" />
                Winning Details
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Winning Amount (₹) *</label>
                  <input
                    type="text"
                    value={formData.winning_amount}
                    onChange={(e) => handleChange("winning_amount", e.target.value)}
                    className="form-input w-full"
                    placeholder="1,00,000"
                    data-testid="winning-amount-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Contests Won</label>
                  <input
                    type="number"
                    value={formData.contests_won}
                    onChange={(e) => handleChange("contests_won", parseInt(e.target.value))}
                    className="form-input w-full"
                    min="1"
                    data-testid="contests-won-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Prize Pool (₹) *</label>
                  <input
                    type="text"
                    value={formData.prize_pool}
                    onChange={(e) => handleChange("prize_pool", e.target.value)}
                    className="form-input w-full"
                    placeholder="30 Lakhs"
                    data-testid="prize-pool-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Spots *</label>
                  <input
                    type="text"
                    value={formData.spots}
                    onChange={(e) => handleChange("spots", e.target.value)}
                    className="form-input w-full"
                    placeholder="14,76,906"
                    data-testid="spots-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Entry Fee (₹)</label>
                  <input
                    type="text"
                    value={formData.entry_fee}
                    onChange={(e) => handleChange("entry_fee", e.target.value)}
                    className="form-input w-full"
                    placeholder="0"
                    data-testid="entry-fee-input"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Rank</label>
                  <input
                    type="number"
                    value={formData.rank}
                    onChange={(e) => handleChange("rank", parseInt(e.target.value))}
                    className="form-input w-full"
                    min="1"
                    data-testid="rank-input"
                  />
                </div>
              </div>
            </div>

            {/* Match Details */}
            <div className="dashboard-card">
              <h2 className="font-['Teko'] text-xl text-white uppercase mb-4 flex items-center gap-2">
                <Calendar size={20} className="text-[#40E0D0]" />
                Match Details
              </h2>
              <div className="mb-4">
                <label className="block text-sm text-[#A1A1AA] mb-2">Match Date</label>
                <input
                  type="text"
                  value={formData.match_date}
                  onChange={(e) => handleChange("match_date", e.target.value)}
                  className="form-input w-full"
                  placeholder="02/11/2025"
                  data-testid="match-date-input"
                />
              </div>

              {/* Team 1 Selection */}
              <div className="mb-4">
                <label className="block text-sm text-[#A1A1AA] mb-2">Team 1 *</label>
                <div className="flex flex-wrap gap-3">
                  {teamLogos.map((logo) => (
                    <div
                      key={logo.id}
                      onClick={() => selectTeamLogo('team1', logo)}
                      className={`logo-card ${formData.team1_name === logo.name ? 'selected' : ''}`}
                      data-testid={`team1-${logo.short_name}`}
                    >
                      <img
                        src={logo.logo_url}
                        alt={logo.name}
                        className="w-12 h-12 mx-auto object-contain"
                        onError={(e) => { e.target.src = 'https://via.placeholder.com/50'; }}
                      />
                      <p className="text-xs text-[#A1A1AA] mt-2">{logo.short_name}</p>
                    </div>
                  ))}
                </div>
                {formData.team1_name && (
                  <p className="text-[#00FF88] text-sm mt-2">Selected: {formData.team1_name}</p>
                )}
              </div>

              {/* Team 2 Selection */}
              <div className="mb-4">
                <label className="block text-sm text-[#A1A1AA] mb-2">Team 2 *</label>
                <div className="flex flex-wrap gap-3">
                  {teamLogos.map((logo) => (
                    <div
                      key={logo.id}
                      onClick={() => selectTeamLogo('team2', logo)}
                      className={`logo-card ${formData.team2_name === logo.name ? 'selected' : ''}`}
                      data-testid={`team2-${logo.short_name}`}
                    >
                      <img
                        src={logo.logo_url}
                        alt={logo.name}
                        className="w-12 h-12 mx-auto object-contain"
                        onError={(e) => { e.target.src = 'https://via.placeholder.com/50'; }}
                      />
                      <p className="text-xs text-[#A1A1AA] mt-2">{logo.short_name}</p>
                    </div>
                  ))}
                </div>
                {formData.team2_name && (
                  <p className="text-[#00FF88] text-sm mt-2">Selected: {formData.team2_name}</p>
                )}
              </div>

              {/* Custom Logo URLs */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-[#333333]">
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Or Enter Team 1 Logo URL</label>
                  <input
                    type="text"
                    value={formData.team1_logo}
                    onChange={(e) => handleChange("team1_logo", e.target.value)}
                    className="form-input w-full text-sm"
                    placeholder="https://..."
                    data-testid="team1-logo-url"
                  />
                </div>
                <div>
                  <label className="block text-sm text-[#A1A1AA] mb-2">Or Enter Team 2 Logo URL</label>
                  <input
                    type="text"
                    value={formData.team2_logo}
                    onChange={(e) => handleChange("team2_logo", e.target.value)}
                    className="form-input w-full text-sm"
                    placeholder="https://..."
                    data-testid="team2-logo-url"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-4">
              <button
                onClick={createCampaign}
                disabled={loading || !isFormValid()}
                className="btn-primary flex-1 flex items-center justify-center gap-2 disabled:opacity-50"
                data-testid="preview-button"
              >
                {loading ? (
                  <Loader2 className="animate-spin" size={20} />
                ) : (
                  <Eye size={20} />
                )}
                {loading ? "Creating..." : "Preview Email"}
              </button>

              {createdCampaignId && (
                <button
                  onClick={sendEmail}
                  disabled={sending}
                  className="btn-primary flex-1 flex items-center justify-center gap-2 bg-[#FF0080] hover:bg-[#CC0066]"
                  style={{ boxShadow: '0 0 20px rgba(255, 0, 128, 0.4)' }}
                  data-testid="send-button"
                >
                  {sending ? (
                    <Loader2 className="animate-spin" size={20} />
                  ) : (
                    <Send size={20} />
                  )}
                  {sending ? "Sending..." : "Send Email"}
                </button>
              )}
            </div>
          </motion.div>

          {/* Preview Section */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:sticky lg:top-24 h-fit"
          >
            <div className="dashboard-card">
              <h2 className="font-['Teko'] text-xl text-white uppercase mb-4 flex items-center gap-2">
                <Mail size={20} className="text-[#00FF88]" />
                Email Preview
              </h2>

              {previewHtml ? (
                <div className="email-preview-container">
                  <iframe
                    srcDoc={previewHtml}
                    title="Email Preview"
                    className="w-full h-[600px] border-0 rounded-lg"
                    data-testid="email-preview-iframe"
                  />
                </div>
              ) : (
                <div className="bg-[#111111] rounded-lg p-8 text-center min-h-[400px] flex flex-col items-center justify-center">
                  <Eye size={48} className="text-[#333333] mb-4" />
                  <p className="text-[#A1A1AA]">
                    Fill the form and click "Preview Email" to see your email
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
