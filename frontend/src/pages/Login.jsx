import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import axios from "axios";
import { motion } from "framer-motion";
import { Eye, EyeOff, Loader2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const COME_LOGO = "https://customer-assets.emergentagent.com/job_cricketapp-5/artifacts/1fb8tcpa_IMG_20260115_162945_452.png";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      toast.error("Please enter username and password");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/login`, {
        username,
        password,
      });
      localStorage.setItem("come_token", response.data.token);
      localStorage.setItem("come_user", response.data.username);
      toast.success("Welcome to COME!");
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00FF88] opacity-5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FF0080] opacity-5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="bg-[#121212] border border-[#333333] rounded-2xl p-8 shadow-2xl">
          {/* Logo */}
          <div className="text-center mb-8">
            <motion.img
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              src={COME_LOGO}
              alt="COME"
              className="w-32 h-32 mx-auto object-contain"
              data-testid="come-logo"
            />
            <h1 className="font-['Teko'] text-3xl text-white mt-4 uppercase tracking-wide">
              Welcome Back
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-2">
              Professional Email Campaign Manager
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm text-[#A1A1AA] mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="form-input w-full"
                placeholder="Enter username"
                data-testid="username-input"
              />
            </div>

            <div>
              <label className="block text-sm text-[#A1A1AA] mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="form-input w-full pr-12"
                  placeholder="Enter password"
                  data-testid="password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white"
                  data-testid="toggle-password"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
              data-testid="login-button"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Logging in...
                </>
              ) : (
                "Login to Dashboard"
              )}
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-[#333333] text-center">
            <p className="text-[#A1A1AA] text-xs">
              Made with ❤️ by COME Team
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
