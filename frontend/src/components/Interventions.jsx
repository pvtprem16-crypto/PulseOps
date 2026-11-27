import { useEffect, useState } from "react";
import {
  Activity,
  ClipboardList,
  CheckCircle2,
  Clock3,
  AlertCircle,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";

const API = "http://127.0.0.1:8000/api/v1/interventions";

const emptyForm = {
  priority: "High",
  client: "Alpha Corp",
  service: "Database Services",
  assigned_team: "Database Team",
  risk_level: "High",
  breach_probability: 78.01,
  action_taken: "",
  owner: "",
  status: "Open",
  notes: "",
};

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <div className="flex justify-between items-center">
        <p className="text-sm text-gray-500">{title}</p>
        <div className={`p-2 rounded-xl ${color}`}>
          <Icon size={20} />
        </div>
      </div>
      <h2 className="text-2xl font-bold mt-3">{value}</h2>
    </div>
  );
}

export default function Interventions() {
  const [records, setRecords] = useState([]);
  const [summary, setSummary] = useState({
    total: 0,
    open: 0,
    in_progress: 0,
    completed: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  async function loadData() {
    setLoading(true);
    setError("");

    try {
      const [recordsResponse, summaryResponse] = await Promise.all([
        fetch(`${API}/`),
        fetch(`${API}/summary`),
      ]);

      if (!recordsResponse.ok || !summaryResponse.ok) {
        throw new Error("Failed to load interventions");
      }

      const recordsData = await recordsResponse.json();
      const summaryData = await summaryResponse.json();

      setRecords(recordsData.interventions || []);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message || "Unable to connect to the backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  function updateForm(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function createRecord(e) {
    e.preventDefault();

    if (!form.action_taken.trim()) {
      alert("Please enter the action taken.");
      return;
    }

    setSaving(true);

    try {
      const response = await fetch(`${API}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          breach_probability: Number(form.breach_probability),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create intervention");
      }

      setForm(emptyForm);
      setShowForm(false);
      await loadData();
    } catch (err) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function updateStatus(id, status) {
    try {
      const response = await fetch(`${API}/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status }),
      });

      if (!response.ok) {
        throw new Error("Status update failed");
      }

      await loadData();
    } catch (err) {
      alert(err.message);
    }
  }

  async function deleteRecord(id) {
    if (!window.confirm("Delete this intervention?")) return;

    try {
      const response = await fetch(`${API}/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Delete failed");
      }

      await loadData();
    } catch (err) {
      alert(err.message);
    }
  }

  const statusStyle = {
    Open: "bg-amber-100 text-amber-700",
    "In Progress": "bg-blue-100 text-blue-700",
    Completed: "bg-emerald-100 text-emerald-700",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 text-sm font-medium">
            <Activity size={16} />
            Operational Intelligence
          </div>
          <h1 className="text-2xl font-bold mt-1">Intervention Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Track actions taken to prevent SLA breaches.
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={loadData}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border bg-white hover:bg-gray-50"
          >
            <RefreshCw size={16} /> Refresh
          </button>

          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-700"
          >
            <Plus size={16} /> Add Intervention
          </button>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard
          title="Total Interventions"
          value={summary.total}
          icon={ClipboardList}
          color="bg-indigo-100 text-indigo-600"
        />
        <StatCard
          title="Open"
          value={summary.open}
          icon={AlertCircle}
          color="bg-amber-100 text-amber-600"
        />
        <StatCard
          title="In Progress"
          value={summary.in_progress}
          icon={Clock3}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          title="Completed"
          value={summary.completed}
          icon={CheckCircle2}
          color="bg-emerald-100 text-emerald-600"
        />
      </div>

      {/* Form */}
      {showForm && (
        <form
          onSubmit={createRecord}
          className="bg-white rounded-2xl border shadow-sm p-6 space-y-4"
        >
          <h2 className="text-lg font-semibold">Create Intervention</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              ["priority", "Priority"],
              ["client", "Client"],
              ["service", "Service"],
              ["assigned_team", "Assigned Team"],
              ["risk_level", "Risk Level"],
              ["owner", "Action Owner"],
            ].map(([key, label]) => (
              <div key={key}>
                <label className="block text-sm mb-1 text-gray-600">
                  {label}
                </label>
                <input
                  value={form[key]}
                  onChange={(e) => updateForm(key, e.target.value)}
                  className="w-full border rounded-xl px-3 py-2"
                  required={key !== "owner"}
                />
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm mb-1 text-gray-600">
              Breach Probability (%)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={form.breach_probability}
              onChange={(e) =>
                updateForm("breach_probability", e.target.value)
              }
              className="w-full border rounded-xl px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1 text-gray-600">
              Action Taken
            </label>
            <input
              value={form.action_taken}
              onChange={(e) => updateForm("action_taken", e.target.value)}
              placeholder="e.g. Escalated to database specialist"
              className="w-full border rounded-xl px-3 py-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1 text-gray-600">Notes</label>
            <textarea
              value={form.notes}
              onChange={(e) => updateForm("notes", e.target.value)}
              rows={3}
              className="w-full border rounded-xl px-3 py-2"
              placeholder="Additional details..."
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={saving}
              className="bg-indigo-600 text-white px-5 py-2 rounded-xl disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Intervention"}
            </button>

            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="border px-5 py-2 rounded-xl"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Table */}
      <div className="bg-white rounded-2xl border shadow-sm overflow-hidden">
        <div className="p-5 border-b">
          <h2 className="font-semibold">Recorded Interventions</h2>
        </div>

        {loading ? (
          <div className="p-10 text-center text-gray-500">Loading...</div>
        ) : error ? (
          <div className="p-10 text-center text-red-500">{error}</div>
        ) : records.length === 0 ? (
          <div className="p-10 text-center text-gray-500">
            No interventions recorded yet.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-500">
                <tr>
                  {[
                    "Date",
                    "Priority",
                    "Client",
                    "Service",
                    "Team",
                    "Probability",
                    "Action",
                    "Owner",
                    "Status",
                    "",
                  ].map((header) => (
                    <th key={header} className="text-left p-4 font-medium">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {records.map((record) => (
                  <tr
                    key={record.intervention_id}
                    className="border-t hover:bg-gray-50"
                  >
                    <td className="p-4 whitespace-nowrap">
                      {record.created_at}
                    </td>
                    <td className="p-4">{record.priority}</td>
                    <td className="p-4">{record.client}</td>
                    <td className="p-4">{record.service}</td>
                    <td className="p-4">{record.assigned_team}</td>
                    <td className="p-4 font-semibold">
                      {Number(record.breach_probability).toFixed(2)}%
                    </td>
                    <td className="p-4 min-w-[200px]">
                      {record.action_taken}
                    </td>
                    <td className="p-4">{record.owner || "-"}</td>
                    <td className="p-4">
                      <select
                        value={record.status}
                        onChange={(e) =>
                          updateStatus(record.intervention_id, e.target.value)
                        }
                        className={`rounded-lg px-3 py-1 text-xs font-medium ${
                          statusStyle[record.status] || ""
                        }`}
                      >
                        <option>Open</option>
                        <option>In Progress</option>
                        <option>Completed</option>
                      </select>
                    </td>
                    <td className="p-4">
                      <button
                        onClick={() => deleteRecord(record.intervention_id)}
                        className="text-red-500 hover:text-red-700"
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
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