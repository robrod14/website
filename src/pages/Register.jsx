import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

export default function Register() {
  const { id } = useParams(); // event ID from URL
  const [event, setEvent] = useState(null);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [status, setStatus] = useState(null);
  const [registration, setRegistration] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch event info
  useEffect(() => {
    async function fetchEvent() {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/events/`);
        const found = res.data.find((e) => e.id === parseInt(id));
        setEvent(found || null);
      } catch (err) {
        console.error(err);
        setError("Failed to load event");
      } finally {
        setLoading(false);
      }
    }
    fetchEvent();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!name || !phone) {
      setError("Please enter both name and phone");
      return;
    }

    try {
      const res = await axios.post(`http://127.0.0.1:5000/events/${id}/register`, {
        name,
        phone,
      });
      setRegistration(res.data);
      setStatus(res.data.status);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Registration failed");
    }
  };

  if (loading) return <div className="mt-10 text-center">Loading event...</div>;
  if (!event) return <div className="mt-10 text-center text-red-500">Event not found</div>;

  return (
    <div className="max-w-md mx-auto bg-white shadow-md rounded p-6 mt-6">
      <h1 className="text-2xl font-bold mb-4">{event.title}</h1>
      <p className="text-gray-600 mb-1">{event.location}</p>
      <p className="text-gray-600 mb-4">
        {event.date} at {event.time}
      </p>

      {!registration ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <p className="text-red-500">{error}</p>}
          <div>
            <label className="block text-gray-700">Name</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2 mt-1"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-gray-700">Phone</label>
            <input
              type="text"
              className="w-full border rounded px-3 py-2 mt-1"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            Register
          </button>
        </form>
      ) : (
        <div className="mt-6 p-4 bg-green-50 border-l-4 border-green-500">
          <p className="font-semibold">
            Registration Status:{" "}
            <span className={status === "registered" ? "text-green-700" : "text-yellow-700"}>
              {status.toUpperCase()}
            </span>
          </p>
          {status === "pending_payment" && (
            <div className="mt-4">
              <p className="mb-2">Scan this QR code to pay via Venmo:</p>
              <img
                src={`http://127.0.0.1:5000/payment/qr/${registration.registration_id}`}
                alt="Venmo QR"
                className="w-40 h-40"
              />
              <p className="mt-2 text-sm text-gray-700">
                Payment Memo: {registration.payment_memo}
              </p>
            </div>
          )}
          {status === "waitlist" && (
            <p className="mt-2 text-gray-700">You are on the waitlist. You will be notified if a spot opens.</p>
          )}
        </div>
      )}
    </div>
  );
}
