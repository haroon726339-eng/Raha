import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Send,
  Trash2,
  Eye,
  Mail,
  CheckCircle,
  Clock,
  XCircle,
  Loader2,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COME_LOGO = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png";

export default function CampaignHistory() {
  const navigate = useNavigate();
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewHtml, setPreviewHtml] = useState("");
  const [previewCampaign, setPreviewCampaign] = useState(null);
  const [sendingId, setSendingId] = useState(null);

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("come_token")}`,
  });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API}/campaigns`, { headers: getAuthHeaders() });
      setCampaigns(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        navigate("/login");
      }
      toast.error("Failed to fetch campaigns");
    } finally {
      setLoading(false);
    }
  };

  const deleteCampaign = async (campaignId) => {
    if (!window.confirm("Are you sure you want to delete this campaign?")) return;

    try {
      await axios.delete(`${API}/campaigns/${campaignId}`, { headers: getAuthHeaders() });
      toast.success("Campaign deleted");
      fetchCampaigns();
    } catch (error) {
      toast.error("Failed to delete campaign");
    }
  };

  const previewEmail = async (campaign) => {
    try {
      const response = await axios.post(
        `${API}/campaigns/${campaign.id}/preview`,
        {},
        { headers: getAuthHeaders() }
      );
      setPreviewHtml(response.data.html);
      setPreviewCampaign(campaign);
    } catch (error) {
      toast.error("Failed to load preview");
    }
  };

  const sendEmail = async (campaignId) => {
    setSendingId(campaignId);
    try {
      await axios.post(
        `${API}/campaigns/${campaignId}/send`,
        {},
        { headers: getAuthHeaders() }
      );
      toast.success("Email sent successfully!");
      fetchCampaigns();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to send email");
    } finally {
      setSendingId(null);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "sent":
        return <CheckCircle size={16} className="text-[#00FF88]" />;
      case "draft":
        return <Clock size={16} className="text-[#FFD700]" />;
      case "failed":
        return <XCircle size={16} className="text-[#FF4444]" />;
      default:
        return null;
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
            <h1 className="font-['Teko'] text-xl text-white uppercase">Campaign History</h1>
          </div>

          <Link
            to="/create"
            className="btn-primary flex items-center gap-2 text-sm py-2 px-4"
            data-testid="new-campaign-button"
          >
            <Mail size={16} />
            New Campaign
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center py-16">
            <Loader2 className="animate-spin mx-auto text-[#00FF88]" size={48} />
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-16">
            <Mail size={64} className="mx-auto text-[#333333] mb-4" />
            <p className="text-[#A1A1AA] mb-4">No campaigns yet</p>
            <Link to="/create" className="text-[#00FF88] hover:underline">
              Create your first campaign
            </Link>
          </div>
        ) : (
          <div className="grid gap-4">
            {campaigns.map((campaign, index) => (
              <motion.div
                key={campaign.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="dashboard-card"
                data-testid={`campaign-card-${campaign.id}`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  {/* Campaign Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`status-${campaign.status} flex items-center gap-1`}>
                        {getStatusIcon(campaign.status)}
                        {campaign.status.toUpperCase()}
                      </span>
                      <span className="text-[#A1A1AA] text-sm">
                        {new Date(campaign.created_at).toLocaleDateString()} at{" "}
                        {new Date(campaign.created_at).toLocaleTimeString()}
                      </span>
                    </div>

                    <h3 className="text-white text-lg font-semibold mb-1">
                      {campaign.winner_name} - ₹{campaign.winning_amount}
                    </h3>

                    <p className="text-[#A1A1AA] text-sm">
                      {campaign.winner_email} •{" "}
                      {campaign.team1_name} vs {campaign.team2_name} •{" "}
                      {campaign.match_date}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => previewEmail(campaign)}
                      className="btn-outline flex items-center gap-2 text-sm py-2 px-4"
                      data-testid={`preview-${campaign.id}`}
                    >
                      <Eye size={16} />
                      Preview
                    </button>

                    {campaign.status === "draft" && (
                      <button
                        onClick={() => sendEmail(campaign.id)}
                        disabled={sendingId === campaign.id}
                        className="btn-primary flex items-center gap-2 text-sm py-2 px-4"
                        data-testid={`send-${campaign.id}`}
                      >
                        {sendingId === campaign.id ? (
                          <Loader2 className="animate-spin" size={16} />
                        ) : (
                          <Send size={16} />
                        )}
                        Send
                      </button>
                    )}

                    <button
                      onClick={() => deleteCampaign(campaign.id)}
                      className="p-2 rounded-lg bg-[#FF4444]/10 text-[#FF4444] hover:bg-[#FF4444]/20 transition-colors"
                      data-testid={`delete-${campaign.id}`}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Preview Modal */}
        {previewCampaign && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-[#121212] border border-[#333333] rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
            >
              <div className="p-4 border-b border-[#333333] flex items-center justify-between">
                <h2 className="font-['Teko'] text-xl text-white uppercase">
                  Email Preview - {previewCampaign.winner_name}
                </h2>
                <button
                  onClick={() => {
                    setPreviewCampaign(null);
                    setPreviewHtml("");
                  }}
                  className="text-[#A1A1AA] hover:text-white"
                  data-testid="close-preview"
                >
                  ✕
                </button>
              </div>

              <div className="email-preview-container overflow-y-auto">
                <iframe
                  srcDoc={previewHtml}
                  title="Email Preview"
                  className="w-full h-[600px] border-0"
                  data-testid="preview-iframe"
                />
              </div>
            </motion.div>
          </div>
        )}
      </main>
    </div>
  );
}
