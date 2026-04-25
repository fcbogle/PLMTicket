import { ChangeEvent, FormEvent, useEffect, useState } from "react";

type Ticket = {
  id: number;
  vendor_ticket_id: string;
  vendor_subject: string | null;
  vendor_from_name: string | null;
  vendor_status: string | null;
  vendor_created_date: string | null;
  vendor_closed_date: string | null;
  vendor_agent_assigned: string | null;
  vendor_issue_category: string | null;
  internal_status: string | null;
  internal_owner: string | null;
  issue_category: string | null;
  root_cause: string | null;
  comments: string | null;
};

type ImportSummary = {
  new: number;
  updated: number;
  failed: number;
  errors: string[];
};

const API_BASE = "http://localhost:8000";

const emptyFilters = { q: "", status: "", category: "" };
const internalStatusOptions = ["", "New", "In Review", "Waiting On Vendor", "Blocked", "Closed"];
const issueCategoryOptions = [
  "",
  "User Experience",
  "Training",
  "Workshop Required",
  "Data Quality",
  "Access Request",
  "Configuration",
  "Process Design",
  "Reporting",
  "Integration",
  "Other",
];

function formatDate(value: string | null) {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function normalizeStatus(value: string | null) {
  return (value ?? "").trim().toLowerCase();
}

function statusTone(value: string | null) {
  const normalized = normalizeStatus(value);
  if (!normalized) return "neutral";
  if (normalized === "closed") return "closed";
  if (normalized.includes("waiting")) return "waiting";
  if (normalized.includes("review")) return "review";
  if (normalized.includes("blocked")) return "blocked";
  if (normalized.includes("open") || normalized.includes("new")) return "open";
  return "neutral";
}

function categoryTone(value: string | null) {
  const normalized = (value ?? "").trim().toLowerCase();
  if (!normalized) return "neutral";
  if (normalized.includes("training")) return "training";
  if (normalized.includes("data")) return "data";
  if (normalized.includes("access")) return "access";
  if (normalized.includes("process")) return "process";
  return "neutral";
}

function App() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [filters, setFilters] = useState(emptyFilters);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string>("");
  const [messageType, setMessageType] = useState<"success" | "error" | "info">("info");
  const openTickets = tickets.filter((ticket) => normalizeStatus(ticket.vendor_status) !== "closed").length;
  const enrichedTickets = tickets.filter((ticket) => ticket.issue_category || ticket.internal_status || ticket.comments).length;

  async function loadTickets() {
    setLoading(true);
    const params = new URLSearchParams();
    if (filters.q) params.set("q", filters.q);
    if (filters.status) params.set("status", filters.status);
    if (filters.category) params.set("category", filters.category);

    const response = await fetch(`${API_BASE}/tickets?${params.toString()}`);
    const data = (await response.json()) as Ticket[];
    setTickets(data);
    setSelectedTicket((current) => data.find((ticket) => ticket.id === current?.id) ?? data[0] ?? null);
    setLoading(false);
  }

  useEffect(() => {
    void loadTickets();
  }, []);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setMessageType("error");
      setMessage("Select a CSV file first.");
      return;
    }

    setLoading(true);
    setMessageType("info");
    setMessage("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await fetch(`${API_BASE}/imports/csv`, {
      method: "POST",
      body: formData,
    });

    const data = (await response.json()) as ImportSummary | { detail: string };
    if (!response.ok) {
      setMessageType("error");
      setMessage("detail" in data ? data.detail : "Import failed.");
      setLoading(false);
      return;
    }

    const summary = data as ImportSummary;
    setMessageType("success");
    setMessage(`Imported ${summary.new} new, updated ${summary.updated}, failed ${summary.failed}.`);
    await loadTickets();
    setLoading(false);
  }

  async function handleSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedTicket) return;

    setSaving(true);
    setMessageType("info");
    setMessage(`Saving updates for ${selectedTicket.vendor_ticket_id}...`);

    const response = await fetch(`${API_BASE}/tickets/${selectedTicket.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        internal_status: selectedTicket.internal_status,
        internal_owner: selectedTicket.internal_owner,
        issue_category: selectedTicket.issue_category,
        root_cause: selectedTicket.root_cause,
        comments: selectedTicket.comments,
      }),
    });

    if (!response.ok) {
      const error = (await response.json()) as { detail?: string };
      setMessageType("error");
      setMessage(error.detail ?? `Save failed for ${selectedTicket.vendor_ticket_id}.`);
      setSaving(false);
      return;
    }

    const updated = (await response.json()) as Ticket;
    setSelectedTicket(updated);
    setTickets((current) => current.map((ticket) => (ticket.id === updated.id ? updated : ticket)));
    setMessageType("success");
    setMessage(`Saved updates for ${updated.vendor_ticket_id}.`);
    setSaving(false);
  }

  function updateSelected<K extends keyof Ticket>(field: K, value: Ticket[K]) {
    setSelectedTicket((current) => (current ? { ...current, [field]: value } : current));
  }

  function handleFilterChange(event: ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  }

  return (
    <div className="shell">
      <header className="top-nav">
        <div className="brand-block">
          <div className="nav-brand-row">
            <img className="nav-logo" src="/blatchford-mark.jpeg" alt="Blatchford logo" />
            <div className="nav-title-block">
              <strong>PLM Ticket Manager</strong>
              <span className="nav-subtitle">Blatchford support oversight and enrichment workspace</span>
            </div>
          </div>
          <span className="brand-kicker">PLM Support Operations</span>
        </div>
        <a className="export-link" href={`${API_BASE}/exports/excel`}>
          Export Excel
        </a>
      </header>

      <section className="hero">
        <div className="hero-copy-block">
          <p className="eyebrow">Vendor Intake And Internal Review</p>
          <h1>Bring external PLM tickets into a branded internal review flow.</h1>
          <p className="lede">
            Upload the vendor CSV, preserve internal categorisation and notes, and export a clean workbook for management
            review.
          </p>
        </div>
        <div className="hero-stats">
          <div className="stat-card">
            <span className="stat-label">Tickets Loaded</span>
            <strong>{tickets.length}</strong>
          </div>
          <div className="stat-card">
            <span className="stat-label">Open Tickets</span>
            <strong>{openTickets}</strong>
          </div>
          <div className="stat-card">
            <span className="stat-label">Enriched Tickets</span>
            <strong>{enrichedTickets}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <h2>Import And Filter</h2>
          <span>CSV upload, search, and list refresh</span>
        </div>
        <form className="upload-form" onSubmit={handleUpload}>
          <input type="file" accept=".csv" onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)} />
          <button type="submit" disabled={loading}>
            Upload CSV
          </button>
        </form>
        <form
          className="filters"
          onSubmit={(event) => {
            event.preventDefault();
            void loadTickets();
          }}
        >
          <input name="q" placeholder="Search ticket or subject" value={filters.q} onChange={handleFilterChange} />
          <input name="status" placeholder="Filter status" value={filters.status} onChange={handleFilterChange} />
          <input name="category" placeholder="Filter category" value={filters.category} onChange={handleFilterChange} />
          <button type="submit" disabled={loading}>
            Apply
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setFilters(emptyFilters);
              setTimeout(() => void loadTickets(), 0);
            }}
            disabled={loading}
          >
            Clear
          </button>
        </form>
        {message ? <p className={`message message-${messageType}`}>{message}</p> : null}
      </section>

      <main className="layout">
        <section className="panel table-panel">
          <div className="panel-header">
            <h2>Tickets</h2>
            <span>{loading ? "Loading..." : `${tickets.length} records`}</span>
          </div>
          <table>
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Subject</th>
                <th>Vendor Status</th>
                <th>Internal Status</th>
                <th>Vendor Category</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((ticket) => (
                <tr
                  key={ticket.id}
                  className={selectedTicket?.id === ticket.id ? "selected-row" : ""}
                  onClick={() => setSelectedTicket(ticket)}
                >
                  <td>{ticket.vendor_ticket_id}</td>
                  <td>{ticket.vendor_subject}</td>
                  <td>
                    <span className={`pill pill-${statusTone(ticket.vendor_status)}`}>{ticket.vendor_status ?? "n/a"}</span>
                  </td>
                  <td>
                    <span className={`pill pill-${statusTone(ticket.internal_status)}`}>{ticket.internal_status ?? "n/a"}</span>
                  </td>
                  <td>
                    <span className={`pill pill-${categoryTone(ticket.vendor_issue_category)}`}>
                      {ticket.vendor_issue_category ?? "n/a"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="panel detail-panel">
          <div className="panel-header">
            <h2>Ticket Detail</h2>
            <span>{selectedTicket ? formatDate(selectedTicket.vendor_created_date) : "Select a ticket"}</span>
          </div>
          {selectedTicket ? (
            <form className="detail-form" onSubmit={handleSave}>
              <div className="meta-grid">
                <div>
                  <label>Ticket ID</label>
                  <p>{selectedTicket.vendor_ticket_id}</p>
                </div>
                <div>
                  <label>Vendor Status</label>
                  <p>
                    <span className={`pill pill-${statusTone(selectedTicket.vendor_status)}`}>
                      {selectedTicket.vendor_status ?? "n/a"}
                    </span>
                  </p>
                </div>
                <div>
                  <label>Assigned Agent</label>
                  <p>{selectedTicket.vendor_agent_assigned ?? "n/a"}</p>
                </div>
                <div>
                  <label>Vendor Category</label>
                  <p>
                    <span className={`pill pill-${categoryTone(selectedTicket.vendor_issue_category)}`}>
                      {selectedTicket.vendor_issue_category ?? "n/a"}
                    </span>
                  </p>
                </div>
                <div>
                  <label>Raised By</label>
                  <p>{selectedTicket.vendor_from_name ?? "n/a"}</p>
                </div>
                <div>
                  <label>Closed Date</label>
                  <p>{formatDate(selectedTicket.vendor_closed_date)}</p>
                </div>
              </div>

              <div>
                <label>Subject</label>
                <p>{selectedTicket.vendor_subject ?? "n/a"}</p>
              </div>

              <label>
                Internal Status
                <select
                  value={selectedTicket.internal_status ?? ""}
                  onChange={(event) => updateSelected("internal_status", event.target.value)}
                >
                  {internalStatusOptions.map((option) => (
                    <option key={option || "blank"} value={option}>
                      {option || "Select status"}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Internal Owner
                <input
                  value={selectedTicket.internal_owner ?? ""}
                  onChange={(event) => updateSelected("internal_owner", event.target.value)}
                />
              </label>
              <label>
                Issue Category
                <select
                  value={selectedTicket.issue_category ?? ""}
                  onChange={(event) => updateSelected("issue_category", event.target.value)}
                >
                  {issueCategoryOptions.map((option) => (
                    <option key={option || "blank"} value={option}>
                      {option || "Select category"}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Root Cause
                <input
                  value={selectedTicket.root_cause ?? ""}
                  onChange={(event) => updateSelected("root_cause", event.target.value)}
                />
              </label>
              <label>
                Comments
                <textarea
                  rows={6}
                  value={selectedTicket.comments ?? ""}
                  onChange={(event) => updateSelected("comments", event.target.value)}
                />
              </label>
              <button type="submit" disabled={saving}>
                {saving ? "Saving..." : "Save Internal Fields"}
              </button>
            </form>
          ) : (
            <p>No tickets loaded yet.</p>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
