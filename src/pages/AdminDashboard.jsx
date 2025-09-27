// frontend/src/pages/AdminDashboard.jsx
import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const [events, setEvents] = useState([]);
  const navigate = useNavigate();

  // ✅ Fetch events for management
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:5000/api/events", {
          withCredentials: true,
        });
        setEvents(res.data);
      } catch (err) {
        console.error("Failed to load events", err);
      }
    };
    fetchEvents();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>

      <button
        onClick={() => navigate("/admin/create-event")}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mb-6"
      >
        ➕ Create New Event
      </button>

      <h2 className="text-xl font-semibold mb-2">Your Events</h2>
      {events.length === 0 ? (
        <p>No events created yet.</p>
      ) : (
        <ul className="space-y-2">
          {events.map((event) => (
            <li
              key={event.id}
              className="border p-3 rounded bg-gray-50 flex justify-between items-center"
            >
              <span>
                <strong>{event.name}</strong> – {event.date}
              </span>
              <div className="space-x-2">
                <button
                  onClick={() => navigate(`/admin/edit-event/${event.id}`)}
                  className="bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600"
                >
                  Edit
                </button>
                <button
                  onClick={() => navigate(`/admin/manage-registrations/${event.id}`)}
                  className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                >
                  Registrations
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
