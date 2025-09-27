// frontend/src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const navigate = useNavigate();
  const { isAdmin, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/"); // Back to Events page
    } catch (err) {
      console.error("Logout failed", err);
    }
  };

  return (
    <nav className="bg-gray-900 text-white p-4 flex justify-between">
      <h1 className="font-bold">My Event App</h1>
      <div className="space-x-4">
        <Link to="/" className="hover:underline">
          Events
        </Link>

        {!isAdmin ? (
          <Link to="/admin/login" className="hover:underline">
            Admin
          </Link>
        ) : (
          <>
            <Link to="/admin/dashboard" className="hover:underline">
              Dashboard
            </Link>
            <button
              onClick={handleLogout}
              className="bg-red-600 px-3 py-1 rounded hover:bg-red-700 transition"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
