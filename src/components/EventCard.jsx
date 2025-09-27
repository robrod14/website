import { Link } from "react-router-dom";

export default function EventCard({ event }) {
  return (
    <div className="border rounded-lg p-4 shadow-md bg-white hover:shadow-lg transition-shadow">
      <h2 className="text-xl font-semibold mb-1">{event.title}</h2>
      <p className="text-gray-600 mb-1">{event.location}</p>
      <p className="text-gray-600 mb-1">
        {event.date} at {event.time}
      </p>
      <p className="text-gray-600 mb-2">
        Price: ${(event.price_cents / 100).toFixed(2)} | Capacity: {event.capacity}
      </p>

      {event.is_signups_open ? (
        <Link
          to={`/events/${event.id}/register`}
          className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
        >
          Register
        </Link>
      ) : (
        <span className="text-red-500 font-semibold">Signups Closed</span>
      )}
    </div>
  );
}
