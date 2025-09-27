// frontend/src/context/AuthContext.jsx
import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAdmin, setIsAdmin] = useState(false);

  // ✅ Check if an admin session already exists (e.g. page reload)
  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/admin/me", {
          withCredentials: true,
        });
        setIsAdmin(res.data.is_admin === true);
      } catch {
        setIsAdmin(false);
      }
    };

    checkSession();
  }, []);

  // ✅ Login function (call after login API succeeds)
  const login = () => {
    setIsAdmin(true);
  };

  // ✅ Logout function
  const logout = async () => {
    try {
      await axios.post("http://127.0.0.1:5000/api/admin/logout", {}, { withCredentials: true });
    } catch (err) {
      console.error("Logout failed:", err);
    }
    setIsAdmin(false);
  };

  return (
    <AuthContext.Provider value={{ isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
