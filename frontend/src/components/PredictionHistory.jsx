
import { useEffect, useState } from "react";
import {
  History,
  RefreshCw,
  AlertTriangle,
  ShieldCheck,
  Activity,
} from "lucide-react";

const API = "http://127.0.0.1:8000/api/v1/prediction-history";

export default function PredictionHistory() {
  const [summary, setSummary] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("All");

  async function loadHistory() {
    setLoading(true);
    setError("");

    try {
      const [historyResponse, summaryResponse] = await Promise.all([
        fetch(`${API}/`),
        fetch(`${API}/summary`),
      ]);

      if (!historyResponse.ok || !summaryResponse.ok) {
        throw new Error("Failed to load prediction history.");
      }

      const historyData = await historyResponse.json();
      const summaryData = await summaryResponse.json();

      setPredictions(historyData.predictions || []);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message || "Unable to load history.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  const filteredPredictions =
    filter === "All"
      ? predictions
      : predictions.filter(
          (prediction) => prediction.risk_level === filter
        );

  const riskColor = (risk) => {
    if (risk === "High")
      return "bg-rose-100 text-rose-700";

    if (risk === "Moderate")
      return "bg-amber-100 text-amber-700";

    return "bg-emerald-100 text-emerald-700";
  };

  return (
    <div className="mt-8 space-y-6">

      {/* HEADER */}

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600">
            <History size={20} />
            <span className="font-semibold">Risk Monitoring</span>
          </div>

          <h2 className="mt-2 text-2xl font-bold text-gray-900">
            Prediction History
          </h2>

          <p className="mt-1 text-sm text-gray-500">
            Review previously generated SLA risk predictions.
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* SUMMARY CARDS */}

      {summary && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

          <SummaryCard
            title="Total Predictions"
            value={summary.total_predictions}
            icon={<Activity size={20} />}
            color="text-indigo-600"
            bg="bg-indigo-50"
          />

          <SummaryCard
            title="High Risk"
            value={summary.high_risk}
            icon={<AlertTriangle size={20} />}
            color="text-rose-600"
            bg="bg-rose-50"
          />

          <SummaryCard
            title="Moderate Risk"
            value={summary.moderate_risk}
            icon={<Activity size={20} />}
            color="text-amber-600"
            bg="bg-amber-50"
          />

          <SummaryCard
            title="Low Risk"
            value={summary.low_risk}
            icon={<ShieldCheck size={20} />}
            color="text-emerald-600"
            bg="bg-emerald-50"
          />

        </div>
      )}

      {/* AVERAGE PROBABILITY */}

      {summary && (
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">

            <div>
              <p className="text-sm text-gray-500">
                Average Predicted Breach Probability
              </p>

              <h3 className="mt-2 text-2xl font-bold text-gray-900">
                {(summary.average_breach_probability * 100).toFixed(2)}%
              </h3>
            </div>

            <div className="rounded-xl bg-indigo-50 p-3 text-indigo-600">
              <Activity size={22} />
            </div>

          </div>
        </div>
      )}

      {/* TABLE */}

      <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">

        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-semibold text-gray-900">
            Recorded Predictions
          </h3>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm outline-none focus:border-indigo-500"
          >
            <option value="All">All Risk Levels</option>
            <option value="High">High Risk</option>
            <option value="Moderate">Moderate Risk</option>
            <option value="Low">Low Risk</option>
          </select>
        </div>

        {loading ? (
          <p className="py-10 text-center text-sm text-gray-500">
            Loading prediction history...
          </p>
        ) : error ? (
          <p className="py-10 text-center text-sm text-rose-600">
            {error}
          </p>
        ) : filteredPredictions.length === 0 ? (
          <p className="py-10 text-center text-sm text-gray-500">
            No predictions recorded for this filter.
          </p>
        ) : (

          <div className="overflow-x-auto">
            <table className="w-full min-w-[1000px] text-left text-sm">

              <thead>
                <tr className="border-b border-gray-100 text-gray-500">
                  <th className="px-4 py-3 font-medium">Date</th>
                  <th className="px-4 py-3 font-medium">Priority</th>
                  <th className="px-4 py-3 font-medium">Service</th>
                  <th className="px-4 py-3 font-medium">Team</th>
                  <th className="px-4 py-3 font-medium">Client</th>
                  <th className="px-4 py-3 font-medium">Probability</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Model</th>
                </tr>
              </thead>

              <tbody>
                {filteredPredictions.map((p) => (
                  <tr
                    key={p.id}
                    className="border-b border-gray-50 hover:bg-gray-50"
                  >
                    <td className="px-4 py-3 text-gray-500">
                      {p.predicted_at
                        ? new Date(
                            p.predicted_at + " UTC"
                          ).toLocaleString()
                        : "--"}
                    </td>

                    <td className="px-4 py-3 font-medium text-gray-800">
                      {p.priority}
                    </td>

                    <td className="px-4 py-3 text-gray-700">
                      {p.service}
                    </td>

                    <td className="px-4 py-3 text-gray-700">
                      {p.assigned_team}
                    </td>

                    <td className="px-4 py-3 text-gray-700">
                      {p.client}
                    </td>

                    <td className="px-4 py-3 font-semibold text-gray-900">
                      {(p.sla_breach_probability * 100).toFixed(2)}%
                    </td>

                    <td className="px-4 py-3">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${riskColor(p.risk_level)}`}
                      >
                        {p.risk_level}
                      </span>
                    </td>

                    <td className="px-4 py-3 text-gray-600">
                      {p.model}
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryCard({ title, value, icon, color, bg }) {
  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">

      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>

          <h3 className="mt-2 text-2xl font-bold text-gray-900">
            {value}
          </h3>
        </div>

        <div className={`rounded-xl p-3 ${bg} ${color}`}>
          {icon}
        </div>
      </div>

    </div>
  );
}
