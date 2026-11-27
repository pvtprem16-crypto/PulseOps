
import { useState } from "react";
import {
  BrainCircuit,
  AlertTriangle,
  ShieldCheck,
  LoaderCircle,
  ArrowLeft,
  Lightbulb,
  ListChecks,
  Activity,
} from "lucide-react";

import PredictionHistory from "./PredictionHistory";

const initialForm = {
  priority: "High",
  client: "Alpha Corp",
  service: "Database Services",
  category: "Database",
  subcategory: "Query Failure",
  assigned_team: "Database Team",
  channel: "Portal",
  created_hour: 14,
  created_day_of_week: 2,
  created_month: 11,
};

const options = {
  priority: ["Critical", "High", "Medium", "Low"],
  client: ["Alpha Corp", "Beta Ltd", "Gamma Inc", "Delta Solutions", "Omega Systems"],
  service: [
    "End User Support",
    "Email Services",
    "Database Services",
    "Business Applications",
    "Network Infrastructure",
  ],
  category: ["Network", "Software", "Email", "Hardware", "Database", "Access"],
  subcategory: [
    "Permission",
    "VPN",
    "DNS",
    "Installation",
    "Wi-Fi",
    "Spam",
    "Peripheral",
    "License",
    "Laptop",
    "Delivery",
    "Connectivity",
    "Printer",
    "Application Error",
    "Performance",
    "Mailbox",
    "Desktop",
    "Connection",
    "Query Failure",
    "Password Reset",
    "Account Lock",
  ],
  assigned_team: [
    "Application Team",
    "Database Team",
    "Network Team",
    "Security Team",
    "Service Desk",
  ],
  channel: ["Phone", "Email", "Monitoring", "Portal"],
};

const days = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

function Field({ label, name, value, onChange, choices }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-gray-700">
        {label}
      </label>

      <select
        name={name}
        value={value}
        onChange={onChange}
        className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
      >
        {choices.map((choice) => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
      </select>
    </div>
  );
}

function generateIndicators(form, riskLevel) {
  const indicators = [];

  if (form.priority === "Critical" || form.priority === "High") {
    indicators.push({
      title: `${form.priority} priority ticket`,
      description:
        "Higher-priority incidents warrant expedited review and careful SLA monitoring.",
    });
  }

  if (form.priority === "Medium") {
    indicators.push({
      title: "Medium priority",
      description:
        "Monitor progress and review escalation needs if resolution is delayed.",
    });
  }

  if (form.priority === "Low") {
    indicators.push({
      title: "Low priority",
      description:
        "Standard queue monitoring may be appropriate, subject to operational conditions.",
    });
  }

  if (form.service === "Database Services") {
    indicators.push({
      title: "Database service",
      description:
        "Check database availability, dependencies and whether specialist support is required.",
    });
  }

  if (form.service === "Network Infrastructure") {
    indicators.push({
      title: "Network infrastructure",
      description:
        "Check connectivity, scope of impact and infrastructure dependencies.",
    });
  }

  if (form.service === "Business Applications") {
    indicators.push({
      title: "Business application",
      description:
        "Check application impact, affected users and dependency on other services.",
    });
  }

  if (form.service === "Email Services") {
    indicators.push({
      title: "Email service",
      description:
        "Review the scope of the email issue and any affected users or systems.",
    });
  }

  if (form.service === "End User Support") {
    indicators.push({
      title: "End-user service",
      description:
        "Confirm user impact and whether a workaround can be provided.",
    });
  }

  if (riskLevel === "High") {
    indicators.push({
      title: "Elevated model-estimated risk",
      description:
        "The model estimates a high probability of resolution SLA breach.",
    });
  }

  if (riskLevel === "Moderate") {
    indicators.push({
      title: "Moderate model-estimated risk",
      description:
        "The model estimates moderate breach risk. Monitor progress proactively.",
    });
  }

  if (riskLevel === "Low") {
    indicators.push({
      title: "Lower model-estimated risk",
      description:
        "The model estimates relatively lower breach risk, though the SLA is not guaranteed.",
    });
  }

  return indicators;
}

function generateRecommendations(form, riskLevel) {
  const recommendations = [];

  if (riskLevel === "High") {
    recommendations.push(
      "Review this ticket as a priority and confirm the remaining SLA time."
    );

    recommendations.push(
      "Consider escalation to the team lead if progress or ownership is uncertain."
    );

    recommendations.push(
      "Monitor ticket progress closely and document the next action."
    );
  } else if (riskLevel === "Moderate") {
    recommendations.push(
      "Monitor progress against the resolution deadline."
    );

    recommendations.push(
      "Review whether additional resources or escalation may be needed."
    );
  } else {
    recommendations.push(
      "Continue standard SLA monitoring and document progress."
    );
  }

  if (form.priority === "Critical") {
    recommendations.push(
      "Confirm incident ownership and assess whether an immediate escalation process applies."
    );
  }

  if (
    form.service === "Database Services" ||
    form.category === "Database"
  ) {
    recommendations.push(
      "Review database dependencies and involve database specialists if required."
    );
  }

  if (
    form.service === "Network Infrastructure" ||
    form.category === "Network"
  ) {
    recommendations.push(
      "Check network dependencies, affected locations and connectivity."
    );
  }

  if (form.assigned_team === "Service Desk") {
    recommendations.push(
      "Assess whether specialist reassignment would help resolve the ticket."
    );
  }

  if (form.channel === "Monitoring") {
    recommendations.push(
      "Review monitoring alerts and correlated incidents for additional context."
    );
  }

  return [...new Set(recommendations)].slice(0, 5);
}

export default function Prediction({ onBack }) {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setResult(null);
    setError("");
  };

  const handlePredict = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setResult(null);

    const payload = {
      ...form,
      created_hour: Number(form.created_hour),
      created_day_of_week: Number(form.created_day_of_week),
      created_month: Number(form.created_month),
    };

    try {
      // STEP 1: GET PREDICTION
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/ml/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Prediction request failed");
      }

      const data = await response.json();

      setResult(data);

      // STEP 2: SAVE PREDICTION TO DATABASE
      try {
        await fetch(
          "http://127.0.0.1:8000/api/v1/prediction-history/",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              ...payload,
              sla_breach_probability: data.sla_breach_probability,
              risk_level: data.risk_level,
              model: data.model,
            }),
          }
        );
      } catch (historyError) {
        console.error(
          "Failed to save prediction history:",
          historyError
        );
      }
    } catch (err) {
      setError(err.message || "Unable to connect to the prediction API.");
    } finally {
      setLoading(false);
    }
  };

  const riskStyles = {
    High: {
      card: "border-rose-200 bg-rose-50",
      text: "text-rose-700",
      icon: "text-rose-600",
      bar: "bg-rose-500",
    },
    Moderate: {
      card: "border-amber-200 bg-amber-50",
      text: "text-amber-700",
      icon: "text-amber-600",
      bar: "bg-amber-500",
    },
    Low: {
      card: "border-emerald-200 bg-emerald-50",
      text: "text-emerald-700",
      icon: "text-emerald-600",
      bar: "bg-emerald-500",
    },
  };

  const indicators = result
    ? generateIndicators(form, result.risk_level)
    : [];

  const recommendations = result
    ? generateRecommendations(form, result.risk_level)
    : [];

  const style = result
    ? riskStyles[result.risk_level] || riskStyles.Moderate
    : riskStyles.Moderate;

  return (
    <div className="space-y-8">
      {/* HEADER */}

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-indigo-600">
            <BrainCircuit size={20} />
            <span className="text-sm font-semibold">
              Predictive Analytics
            </span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900">
            SLA Risk Prediction
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Estimate the probability of a ticket breaching its resolution SLA.
          </p>
        </div>

        {onBack && (
          <button
            onClick={onBack}
            className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
        )}
      </div>

      {/* MAIN PREDICTION LAYOUT */}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">

        {/* FORM */}

        <div className="xl:col-span-2">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-xl bg-indigo-50 p-3">
                <BrainCircuit className="text-indigo-600" size={22} />
              </div>

              <div>
                <h2 className="font-semibold text-gray-900">
                  Ticket Information
                </h2>

                <p className="text-sm text-gray-500">
                  Enter ticket details to calculate risk.
                </p>
              </div>
            </div>

            <form onSubmit={handlePredict} className="space-y-6">

              {/* SELECT FIELDS */}

              <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                {Object.keys(options).map((name) => (
                  <Field
                    key={name}
                    label={name
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (c) => c.toUpperCase())}
                    name={name}
                    value={form[name]}
                    onChange={handleChange}
                    choices={options[name]}
                  />
                ))}
              </div>

              {/* CREATION TIME */}

              <div className="border-t border-gray-100 pt-5">
                <h3 className="mb-4 font-semibold text-gray-900">
                  Ticket Creation Time
                </h3>

                <div className="grid grid-cols-1 gap-5 md:grid-cols-3">

                  {/* HOUR */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Hour (0–23)
                    </label>

                    <input
                      type="number"
                      min="0"
                      max="23"
                      name="created_hour"
                      value={form.created_hour}
                      onChange={handleChange}
                      required
                      className="w-full rounded-xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    />
                  </div>

                  {/* DAY */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Day of Week (0–6)
                    </label>

                    <select
                      name="created_day_of_week"
                      value={form.created_day_of_week}
                      onChange={handleChange}
                      className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    >
                      {days.map((day, index) => (
                        <option key={day} value={index}>
                          {index} - {day}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* MONTH */}

                  <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                      Month
                    </label>

                    <select
                      name="created_month"
                      value={form.created_month}
                      onChange={handleChange}
                      className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    >
                      {months.map((month, index) => (
                        <option key={month} value={index + 1}>
                          {index + 1} - {month}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* ERROR */}

              {error && (
                <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
                  {error}
                </div>
              )}

              {/* SUBMIT */}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3.5 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <LoaderCircle className="animate-spin" size={18} />
                    Calculating Risk...
                  </>
                ) : (
                  <>
                    <BrainCircuit size={18} />
                    Predict SLA Risk
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* RESULTS PANEL */}

        <div className="space-y-5">
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
            <h2 className="mb-5 font-semibold text-gray-900">
              Prediction Result
            </h2>

            {!result ? (
              <div className="flex min-h-64 flex-col items-center justify-center text-center">
                <div className="mb-4 rounded-2xl bg-indigo-50 p-5">
                  <BrainCircuit size={36} className="text-indigo-500" />
                </div>

                <p className="font-medium text-gray-700">
                  No prediction yet
                </p>

                <p className="mt-2 text-sm text-gray-500">
                  Fill in the ticket information and click Predict SLA Risk.
                </p>
              </div>
            ) : (
              <div className="space-y-5">

                {/* RISK CARD */}

                <div className={`rounded-2xl border p-5 ${style.card}`}>
                  <div className="flex items-center gap-2">
                    {result.risk_level === "Low" ? (
                      <ShieldCheck className={style.icon} size={22} />
                    ) : (
                      <AlertTriangle className={style.icon} size={22} />
                    )}

                    <span className={`font-semibold ${style.text}`}>
                      {result.risk_level} Risk
                    </span>
                  </div>

                  <div className="mt-4">
                    <div className={`text-4xl font-bold ${style.text}`}>
                      {result.sla_breach_percentage}%
                    </div>

                    <p className="mt-1 text-sm text-gray-600">
                      Predicted breach probability
                    </p>
                  </div>
                </div>

                {/* PROBABILITY BAR */}

                <div>
                  <div className="mb-2 flex justify-between text-sm">
                    <span className="font-medium text-gray-700">
                      Risk Probability
                    </span>

                    <span className="font-semibold text-gray-900">
                      {result.sla_breach_percentage}%
                    </span>
                  </div>

                  <div className="h-3 overflow-hidden rounded-full bg-gray-100">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${style.bar}`}
                      style={{
                        width: `${result.sla_breach_percentage}%`,
                      }}
                    />
                  </div>
                </div>

                {/* MODEL */}

                <div className="rounded-xl bg-gray-50 p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                    Model Used
                  </p>

                  <p className="mt-1 font-semibold text-gray-800">
                    {result.model}
                  </p>
                </div>

                {/* INTERPRETATION */}

                <div className="rounded-xl border border-gray-100 p-4">
                  <p className="text-sm font-semibold text-gray-800">
                    Suggested interpretation
                  </p>

                  <p className="mt-2 text-sm leading-6 text-gray-600">
                    {result.risk_level === "High"
                      ? "This ticket is flagged as higher risk. Consider prioritizing it for review and proactive intervention."
                      : result.risk_level === "Moderate"
                      ? "This ticket has a moderate estimated risk. Monitor its progress and consider preventive action."
                      : "This ticket has a relatively low estimated risk. Continue standard monitoring."}
                  </p>
                </div>

                {/* RISK INDICATORS */}

                <div className="rounded-2xl border border-indigo-100 bg-indigo-50/50 p-4">
                  <div className="mb-4 flex items-center gap-2">
                    <Activity size={19} className="text-indigo-600" />

                    <h3 className="font-semibold text-gray-900">
                      Risk Indicators
                    </h3>
                  </div>

                  <div className="space-y-3">
                    {indicators.map((indicator, index) => (
                      <div
                        key={index}
                        className="rounded-xl border border-white bg-white p-3"
                      >
                        <p className="text-sm font-semibold text-gray-800">
                          {indicator.title}
                        </p>

                        <p className="mt-1 text-sm leading-5 text-gray-600">
                          {indicator.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* RECOMMENDATIONS */}

                <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4">
                  <div className="mb-4 flex items-center gap-2">
                    <Lightbulb size={19} className="text-emerald-600" />

                    <h3 className="font-semibold text-gray-900">
                      Recommended Actions
                    </h3>
                  </div>

                  <div className="space-y-3">
                    {recommendations.map((recommendation, index) => (
                      <div
                        key={index}
                        className="flex gap-3 rounded-xl border border-white bg-white p-3"
                      >
                        <ListChecks
                          size={18}
                          className="mt-0.5 shrink-0 text-emerald-600"
                        />

                        <p className="text-sm leading-5 text-gray-700">
                          {recommendation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* DISCLAIMER */}

                <p className="text-xs leading-5 text-gray-400">
                  Risk indicators and recommendations are rule-based
                  operational guidance, not explanations of the model's
                  internal decision. This is a model estimate, not a
                  guarantee of SLA outcome. Model performance is limited
                  by the training data.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* PERSISTENT PREDICTION HISTORY */}

      <PredictionHistory />

    </div>
  );
}
