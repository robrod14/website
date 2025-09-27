// frontend/src/components/ProtectedRoute.jsx
import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";

export default function ProtectedRoute({ children }) {
  const [isChecking, setIsChecking] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/admin/me", {
          withCredentials: true,
        });
        if (res.data?.is_admin) {
          setIsAdmin(true);
        } else {
          setIsAdmin(false);
        }
      } catch {
        setIsAdmin(false);
      } finally {
        setIsChecking(false);
      }
    };
    checkAdmin();
  }, []);

  if (isChecking) {
    return <p className="text-center p-4">Checking access...</p>; // ⏳ loading spinner optional
  }

  return isAdmin ? children : <Navigate to="/admin/login" replace />;
}
