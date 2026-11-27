
import { useEffect, useState } from 'react'
import {
  LayoutDashboard,
  Ticket,
  Clock3,
  ChartNoAxesCombined,
  Users,
  Building2,
  Settings,
  Search,
  Bell,
  ChevronDown,
  ArrowUpRight,
  AlertTriangle,
  CheckCircle2,
  CircleHelp,
  Activity,
  Menu,
} from 'lucide-react'

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from 'recharts'

const navItems = [
  { label: 'Dashboard', icon: LayoutDashboard },
  { label: 'Tickets', icon: Ticket },
  { label: 'SLA Analytics', icon: Clock3 },
  { label: 'Team Analytics', icon: Users },
  { label: 'Clients', icon: Building2 },
  { label: 'Insights', icon: ChartNoAxesCombined },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-icon">
          <Activity size={22} />
        </div>
        <div>
          <h1>PulseOps</h1>
          <span>Service Intelligence</span>
        </div>
      </div>

      <div className="nav-section-label">WORKSPACE</div>

      <nav className="navigation">
        {navItems.map((item, index) => {
          const Icon = item.icon

          return (
            <button
              key={item.label}
              className={`nav-item ${index === 0 ? 'active' : ''}`}
            >
              <Icon size={18} />
              <span>{item.label}</span>
              {index === 1 && <span className="nav-count">5k</span>}
            </button>
          )
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="help-card">
          <div className="help-icon">
            <CircleHelp size={18} />
          </div>
          <div>
            <strong>Need help?</strong>
            <p>Explore the platform</p>
          </div>
        </div>

        <button className="nav-item settings-item">
          <Settings size={18} />
          <span>Settings</span>
        </button>

        <div className="profile">
          <div className="avatar">P</div>
          <div className="profile-info">
            <strong>PulseOps Admin</strong>
            <span>Analyst Workspace</span>
          </div>
          <ChevronDown size={16} />
        </div>
      </div>
    </aside>
  )
}

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
  background,
  badge,
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        <div
          className="stat-icon"
          style={{ background, color }}
        >
          <Icon size={21} />
        </div>

        <span className="stat-badge" style={{ color, background }}>
          {badge}
        </span>
      </div>

      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-subtitle">{subtitle}</div>
    </div>
  )
}

function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [apiError, setApiError] = useState('')
  const [priorityData, setPriorityData] = useState([])

  const [activityData, setActivityData] = useState([])
  const [activityLoading, setActivityLoading] = useState(true)
  const [activityError, setActivityError] = useState('')

  const [teamData, setTeamData] = useState([])
  const [teamLoading, setTeamLoading] = useState(true)

  useEffect(() => {
    // Dashboard Overview API
    fetch('http://127.0.0.1:8000/api/v1/dashboard/overview')
      .then((response) => {
        if (!response.ok) throw new Error('Dashboard overview API failed')
        return response.json()
      })
      .then((data) => setOverview(data))
      .catch((error) => {
        console.error(error)
        setApiError(
          'Unable to load dashboard metrics. Check that the backend is running.'
        )
      })
      .finally(() => setLoading(false))

    // Backlog by Priority API
    fetch('http://127.0.0.1:8000/api/v1/backlog/by-priority')
      .then((response) => {
        if (!response.ok) throw new Error('Priority API failed')
        return response.json()
      })
      .then((data) => {
        const colors = {
          Critical: '#ef4444',
          High: '#f59e0b',
          Medium: '#6366f1',
          Low: '#10b981',
        }

        setPriorityData(
          data.priorities.map((item) => ({
            name: item.priority,
            value: item.backlog_tickets,
            color: colors[item.priority] || '#94a3b8',
          }))
        )
      })
      .catch((error) => console.error(error))

    // Ticket Activity API
    fetch('http://127.0.0.1:8000/api/v1/dashboard/activity?days=7')
      .then((response) => {
        if (!response.ok) throw new Error('Ticket activity API failed')
        return response.json()
      })
      .then((data) => setActivityData(data.activity || []))
      .catch((error) => {
        console.error(error)
        setActivityError('Unable to load ticket activity.')
      })
      .finally(() => setActivityLoading(false))

    // Backlog by Team API
    fetch('http://127.0.0.1:8000/api/v1/teams/overview')
      .then((response) => {
        if (!response.ok) throw new Error('Team API failed')
        return response.json()
      })
      .then((data) => {
        const teams = data.teams.map((team) => ({
          name: team.assigned_team.replace(' Team', ''),
          backlog:
            (team.open_tickets || 0) +
            (team.in_progress_tickets || 0) +
            (team.pending_tickets || 0),
        }))

        setTeamData(teams)
      })
      .catch((error) => console.error(error))
      .finally(() => setTeamLoading(false))
  }, [])

  const totalPriorityBacklog = priorityData.reduce(
    (sum, item) => sum + item.value,
    0
  )

  const highPriorityBacklog = priorityData
    .filter((item) => item.name === 'Critical' || item.name === 'High')
    .reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <header className="topbar">
          <button className="mobile-menu">
            <Menu size={20} />
          </button>

          <div className="breadcrumb">
            <span>Workspace</span>
            <span className="breadcrumb-separator">/</span>
            <strong>Dashboard</strong>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <Search size={17} />
              <input placeholder="Search anything..." />
              <kbd>⌘ K</kbd>
            </div>

            <button className="icon-button notification-button">
              <Bell size={19} />
              <span className="notification-dot"></span>
            </button>

            <div className="top-avatar">P</div>
          </div>
        </header>

        <div className="dashboard-content">
          {apiError && <div className="api-error">{apiError}</div>}

          <section className="welcome-section">
            <div>
              <div className="welcome-eyebrow">
                <span className="live-dot"></span>
                SERVICE OPERATIONS OVERVIEW
              </div>

              <h2>Dashboard Overview</h2>

              <p>
                Here's what's happening across your IT service operations.
              </p>
            </div>

            <div className="date-filter">
              <Clock3 size={16} />
              <span>Dataset snapshot</span>
              <ChevronDown size={15} />
            </div>
          </section>

          {/* KPI CARDS */}
          <section className="stats-grid">
            <StatCard
              title="Total Tickets"
              value={
                loading
                  ? '...'
                  : overview
                    ? overview.total_tickets.toLocaleString()
                    : '--'
              }
              subtitle="All tickets in dataset"
              icon={Ticket}
              color="#6366f1"
              background="#eef2ff"
              badge="Dataset"
            />

            <StatCard
              title="Active Backlog"
              value={
                loading
                  ? '...'
                  : overview
                    ? overview.backlog_tickets.toLocaleString()
                    : '--'
              }
              subtitle="Open, pending & in progress"
              icon={Activity}
              color="#f59e0b"
              background="#fff7e6"
              badge={
                loading
                  ? '...'
                  : overview
                    ? `${(
                        (overview.backlog_tickets / overview.total_tickets) *
                        100
                      ).toFixed(1)}% of tickets`
                    : 'Backlog'
              }
            />

            <StatCard
              title="Response SLA"
              value={
                loading
                  ? '...'
                  : overview
                    ? `${overview.response_sla.compliance_percent}%`
                    : '--'
              }
              subtitle={
                loading
                  ? 'Loading metrics...'
                  : overview
                    ? `${overview.response_sla.met_tickets.toLocaleString()} of ${overview.response_sla.eligible_tickets.toLocaleString()} eligible tickets met SLA`
                    : 'API unavailable'
              }
              icon={Clock3}
              color="#0d9488"
              background="#e6fffb"
              badge="Response"
            />

            <StatCard
              title="Resolution SLA"
              value={
                loading
                  ? '...'
                  : overview
                    ? `${overview.resolution_sla.compliance_percent}%`
                    : '--'
              }
              subtitle={
                loading
                  ? 'Loading metrics...'
                  : overview
                    ? `${overview.resolution_sla.met_tickets.toLocaleString()} of ${overview.resolution_sla.eligible_tickets.toLocaleString()} eligible tickets met SLA`
                    : 'API unavailable'
              }
              icon={CheckCircle2}
              color="#e11d48"
              background="#fff1f2"
              badge="Resolution"
            />
          </section>

          {/* MAIN CHARTS */}
          <section className="charts-grid">
            {/* Ticket Activity */}
            <div className="panel tickets-trend-panel">
              <div className="panel-header">
                <div>
                  <h3>Ticket Activity</h3>
                  <p>Tickets created over the last 7 dataset days</p>
                </div>

                <button className="panel-menu">
                  This week <ChevronDown size={15} />
                </button>
              </div>

              <div className="chart-legend">
                <span>
                  <i className="legend-dot tickets-dot"></i>
                  Tickets
                </span>
              </div>

              <div className="trend-chart">
                {activityLoading ? (
                  <div className="chart-message">
                    Loading ticket activity...
                  </div>
                ) : activityError ? (
                  <div className="chart-message">
                    {activityError}
                  </div>
                ) : activityData.length === 0 ? (
                  <div className="chart-message">
                    No ticket activity available.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={activityData}
                      margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient
                          id="ticketGradient"
                          x1="0"
                          y1="0"
                          x2="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#6366f1"
                            stopOpacity={0.22}
                          />
                          <stop
                            offset="100%"
                            stopColor="#6366f1"
                            stopOpacity={0.01}
                          />
                        </linearGradient>
                      </defs>

                      <CartesianGrid stroke="#eef2f7" vertical={false} />

                      <XAxis
                        dataKey="day"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                      />

                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                      />

                      <Tooltip />

                      <Area
                        type="monotone"
                        dataKey="tickets"
                        stroke="#6366f1"
                        strokeWidth={2.5}
                        fill="url(#ticketGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Backlog by Priority */}
            <div className="panel backlog-panel">
              <div className="panel-header">
                <div>
                  <h3>Backlog by Priority</h3>
                  <p>Current backlog distribution</p>
                </div>
              </div>

              <div className="priority-list">
                {priorityData.map((item) => {
                  const total = priorityData.reduce(
                    (sum, current) => sum + current.value,
                    0
                  )

                  return (
                    <div className="priority-item" key={item.name}>
                      <div className="priority-label-row">
                        <div className="priority-label">
                          <span
                            className="priority-dot"
                            style={{ background: item.color }}
                          ></span>
                          {item.name}
                        </div>

                        <strong>{item.value.toLocaleString()}</strong>
                      </div>

                      <div className="priority-track">
                        <div
                          className="priority-fill"
                          style={{
                            width: `${total ? (item.value / total) * 100 : 0}%`,
                            background: item.color,
                          }}
                        ></div>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="priority-footer">
                <div>
                  <span className="priority-total">
                    {totalPriorityBacklog.toLocaleString()}
                  </span>
                  <span className="priority-total-label">Total backlog</span>
                </div>

                <div className="priority-footer-icon">
                  <AlertTriangle size={19} />
                </div>
              </div>
            </div>
          </section>

          {/* BOTTOM CHARTS */}
          <section className="bottom-grid">
            {/* Backlog by Team */}
            <div className="panel teams-panel">
              <div className="panel-header">
                <div>
                  <h3>Backlog by Team</h3>
                  <p>Distribution of pending workload</p>
                </div>

                <button className="panel-menu">
                  View details <ArrowUpRight size={15} />
                </button>
              </div>

              <div className="team-chart">
                {teamLoading ? (
                  <div className="chart-message">
                    Loading team backlog...
                  </div>
                ) : teamData.length === 0 ? (
                  <div className="chart-message">
                    No team data available.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={teamData}
                      layout="vertical"
                      margin={{ top: 0, right: 20, left: 15, bottom: 0 }}
                    >
                      <CartesianGrid stroke="#eef2f7" horizontal={false} />

                      <XAxis
                        type="number"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                      />

                      <YAxis
                        type="category"
                        dataKey="name"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#64748b', fontSize: 12 }}
                        width={100}
                      />

                      <Tooltip />

                      <Bar
                        dataKey="backlog"
                        fill="#6366f1"
                        radius={[0, 6, 6, 0]}
                        barSize={22}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>

            {/* Operational Insight */}
            <div className="panel insight-panel">
              <div className="insight-heading">
                <div className="insight-icon">
                  <ChartNoAxesCombined size={20} />
                </div>
                <div>
                  <h3>Operational Insight</h3>
                  <p>Early warning indicator</p>
                </div>
              </div>

              <div className="insight-highlight">
                <span className="insight-label">
                  HIGH PRIORITY BACKLOG
                </span>
                <h2>{highPriorityBacklog.toLocaleString()} tickets</h2>
                <p>
                  Critical and High priority tickets account for a significant
                  portion of the current backlog.
                </p>
              </div>

              <div className="insight-note">
                <AlertTriangle size={17} />
                <span>
                  Prioritize high-risk tickets to reduce potential service
                  delivery impact.
                </span>
              </div>
            </div>
          </section>

          {/* FOOTER */}
          <footer className="dashboard-footer">
            <span>PulseOps</span>
            <span>IT Service Intelligence & Early-Warning Platform</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
