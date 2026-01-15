import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import { motion } from "framer-motion";
import {
  Mail,
  Send,
  Image,
  Clock,
  Plus,
  LogOut,
  CheckCircle,
  XCircle,
  FileText,
  TrendingUp,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COME_LOGO = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png";

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_campaigns: 0,
    sent_campaigns: 0,
    draft_campaigns: 0,
    failed_campaigns: 0,
    total_logos: 0,
  });
  const [recentCampaigns, setRecentCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const username = localStorage.getItem("come_user") || "User";

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("come_token")}`,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, campaignsRes] = await Promise.all([
        axios.get(`${API}/stats`, { headers: getAuthHeaders() }),
        axios.get(`${API}/campaigns`, { headers: getAuthHeaders() }),
      ]);
      setStats(statsRes.data);
      setRecentCampaigns(campaignsRes.data.slice(0, 5));
    } catch (error) {
      if (error.response?.status === 401) {
        localStorage.removeItem("come_token");
        navigate("/login");
      }
      toast.error("Failed to fetch data");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("come_token");
    localStorage.removeItem("come_user");
    navigate("/login");
    toast.success("Logged out successfully");
  };

  const seedLogos = async () => {
    try {
      const response = await axios.post(`${API}/seed-logos`, {}, { headers: getAuthHeaders() });
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      toast.error("Failed to seed logos");
    }
  };

  const StatCard = ({ icon: Icon, label, value, color, delay }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="dashboard-card card-hover"
      data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[#A1A1AA] text-sm mb-1">{label}</p>
          <p className={`font-['Teko'] text-4xl ${color}`}>{value}</p>
        </div>
        <div className={`p-3 rounded-xl bg-[#1E1E1E]`}>
          <Icon className={color} size={24} />
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Header */}
      <header className="bg-[#121212] border-b border-[#333333] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <img src={COME_LOGO} alt="COME" className="w-12 h-12 object-contain" />
            <div>
              <h1 className="font-['Teko'] text-2xl text-white uppercase">COME</h1>
              <p className="text-[#A1A1AA] text-xs">Email Campaign Manager</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-[#A1A1AA] text-sm">
              Welcome, <span className="text-white font-semibold">{username}</span>
            </span>
            <button
              onClick={handleLogout}
              className="btn-outline flex items-center gap-2 text-sm py-2 px-4"
              data-testid="logout-button"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Mail}
            label="Total Campaigns"
            value={stats.total_campaigns}
            color="text-white"
            delay={0}
          />
          <StatCard
            icon={CheckCircle}
            label="Sent"
            value={stats.sent_campaigns}
            color="text-[#00FF88]"
            delay={0.1}
          />
          <StatCard
            icon={Clock}
            label="Drafts"
            value={stats.draft_campaigns}
            color="text-[#FFD700]"
            delay={0.2}
          />
          <StatCard
            icon={Image}
            label="Total Logos"
            value={stats.total_logos}
            color="text-[#40E0D0]"
            delay={0.3}
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Link
              to="/create"
              className="dashboard-card card-hover flex items-center gap-4 hover:border-[#00FF88]"
              data-testid="create-campaign-link"
            >
              <div className="p-4 rounded-xl bg-[#00FF88]/10">
                <Plus className="text-[#00FF88]" size={28} />
              </div>
              <div>
                <h3 className="font-['Teko'] text-xl text-white uppercase">Create Campaign</h3>
                <p className="text-[#A1A1AA] text-sm">Send winning emails</p>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Link
              to="/logos"
              className="dashboard-card card-hover flex items-center gap-4 hover:border-[#40E0D0]"
              data-testid="manage-logos-link"
            >
              <div className="p-4 rounded-xl bg-[#40E0D0]/10">
                <Image className="text-[#40E0D0]" size={28} />
              </div>
              <div>
                <h3 className="font-['Teko'] text-xl text-white uppercase">Manage Logos</h3>
                <p className="text-[#A1A1AA] text-sm">Team & tournament logos</p>
              </div>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Link
              to="/history"
              className="dashboard-card card-hover flex items-center gap-4 hover:border-[#FFD700]"
              data-testid="view-history-link"
            >
              <div className="p-4 rounded-xl bg-[#FFD700]/10">
                <FileText className="text-[#FFD700]" size={28} />
              </div>
              <div>
                <h3 className="font-['Teko'] text-xl text-white uppercase">View History</h3>
                <p className="text-[#A1A1AA] text-sm">All sent campaigns</p>
              </div>
            </Link>
          </motion.div>
        </div>

        {/* Seed Logos Button (if no logos) */}
        {stats.total_logos === 0 && (
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
              <TrendingUp size={20} />
              Load Default Cricket Team & Tournament Logos
            </button>
          </motion.div>
        )}

        {/* Recent Campaigns */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
          className="dashboard-card"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-['Teko'] text-2xl text-white uppercase">Recent Campaigns</h2>
            <Link to="/history" className="text-[#00FF88] text-sm hover:underline">
              View All
            </Link>
          </div>

          {recentCampaigns.length === 0 ? (
            <div className="text-center py-12">
              <Mail className="mx-auto text-[#333333] mb-4" size={48} />
              <p className="text-[#A1A1AA]">No campaigns yet</p>
              <Link to="/create" className="text-[#00FF88] hover:underline text-sm">
                Create your first campaign
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Winner</th>
                    <th>Match</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentCampaigns.map((campaign) => (
                    <tr key={campaign.id} data-testid={`campaign-row-${campaign.id}`}>
                      <td>
                        <div>
                          <p className="font-medium">{campaign.winner_name}</p>
                          <p className="text-[#A1A1AA] text-sm">{campaign.winner_email}</p>
                        </div>
                      </td>
                      <td>
                        {campaign.team1_name} vs {campaign.team2_name}
                      </td>
                      <td className="text-[#00FF88] font-semibold">
                        ₹{campaign.winning_amount}
                      </td>
                      <td>
                        <span className={`status-${campaign.status}`}>
                          {campaign.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="text-[#A1A1AA] text-sm">
                        {new Date(campaign.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </main>
    </div>
  );
}
