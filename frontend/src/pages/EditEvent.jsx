// frontend/src/pages/EditEvent.jsx
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

export default function EditEvent() {
  const { id } = useParams(); // event ID from URL
  const [event, setEvent] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/events/${id}`);
        setEvent(res.data);
      } catch (err) {
        console.error("Failed to fetch event", err);
      }
    };
    fetchEvent();
  }, [id]);

  const handleChange = (e) => {
    setEvent({ ...event, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.put(
        `http://127.0.0.1:5000/api/events/${id}`,
        event,
        { withCredentials: true }
      );
      navigate("/admin/dashboard"); // back to dashboard
    } catch (err) {
      console.error("Failed to update event", err);
      alert("Update failed");
    }
  };

  if (!event) return <p className="p-6">Loading...</p>;

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Edit Event</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 font-medium">Event Name</label>
          <input
            type="text"
            name="name"
            className="w-full border p-2 rounded"
            value={event.name || ""}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Date</label>
          <input
            type="date"
            name="date"
            className="w-full border p-2 rounded"
            value={event.date ? event.date.split("T")[0] : ""}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Location</label>
          <input
            type="text"
            name="location"
            className="w-full border p-2 rounded"
            value={event.location || ""}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Description</label>
          <textarea
            name="description"
            className="w-full border p-2 rounded"
            rows="4"
            value={event.description || ""}
            onChange={handleChange}
          />
        </div>

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Save Changes
        </button>
      </form>
    </div>
  );
}
