import { useEffect, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useUser } from "@/hooks/useAuth";
import { useInquiries, type Inquiry } from "@/hooks/useInquiries";
import { api } from "@/lib/api";

type Countable = { results?: unknown[]; count?: number } | unknown[];
function count(data: Countable) { return Array.isArray(data) ? data.length : data.count ?? data.results?.length ?? 0; }

const baseApi = import.meta.env.VITE_API_BASE_URL || "/api/v1";
const djangoAdminUrl = baseApi.replace(/\/api\/v1\/?$/, "") + "/admin/";

function InquiryReview({ inquiry, onSaved }: { inquiry: Inquiry; onSaved: () => Promise<void> }) {
  const [response, setResponse] = useState(inquiry.admin_response || "");
  const [status, setStatus] = useState<Inquiry["status"]>(inquiry.status);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState("");

  async function save() {
    setWorking(true); setError("");
    try {
      await api.patch(`/projects/inquiries/${inquiry.id}/`, { admin_response: response, status });
      await onSaved();
    } catch {
      setError("Response could not be saved.");
    } finally {
      setWorking(false);
    }
  }

  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><p className="text-xs font-semibold uppercase tracking-wider text-brand-600">{inquiry.project_title || inquiry.hackathon_title || "Platform support"}</p><h3 className="mt-2 font-display text-xl font-semibold text-slate-900">{inquiry.subject}</h3><p className="mt-1 text-xs text-slate-500">{inquiry.created_by_name} - {inquiry.created_by_email}</p></div>
        <span className={`pill capitalize ${inquiry.status === "open" ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>{inquiry.status}</span>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-600">{inquiry.message}</p>
      <label className="mt-5 block text-sm font-semibold text-slate-700">Organizer response
        <textarea rows={4} value={response} onChange={(event) => setResponse(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="Give the participant a clear next step." />
      </label>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <select value={status} onChange={(event) => setStatus(event.target.value as Inquiry["status"])} className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm">
          <option value="open">Open</option><option value="answered">Answered</option><option value="closed">Closed</option>
        </select>
        <Button type="button" size="sm" disabled={working || !response.trim()} onClick={() => void save()}>{working ? "Saving..." : "Send response"}</Button>
        {error ? <span className="text-xs text-red-600">{error}</span> : null}
      </div>
    </article>
  );
}

export default function AdminDashboardPage() {
  const { user, loading: userLoading } = useUser();
  const { inquiries, loading: inquiriesLoading, refetch } = useInquiries();
  const [stats, setStats] = useState({ hackathons: 0, registrations: 0, problems: 0, teams: 0, projects: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user?.is_staff) { setLoading(false); return; }
    let active = true;
    Promise.all([
      api.get<Countable>("/hackathons/"),
      api.get<Countable>("/hackathons/enrollments/"),
      api.get<Countable>("/hackathons/problems/"),
      api.get<Countable>("/teams/"),
      api.get<Countable>("/projects/?is_public=false"),
    ]).then(([hackathons, registrations, problems, teams, projects]) => {
      if (active) setStats({ hackathons: count(hackathons), registrations: count(registrations), problems: count(problems), teams: count(teams), projects: count(projects) });
    }).catch(() => { if (active) setError("Admin data could not be loaded."); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [user?.is_staff]);

  if (!userLoading && !user?.is_staff) {
    return <section className="py-20"><Container size="sm" className="text-center"><h1 className="font-display text-3xl font-bold text-slate-900">Organizer access only</h1><p className="mt-3 text-slate-600">This workspace is limited to KPITB event staff.</p><Button to="/dashboard" className="mt-7">Back to dashboard</Button></Container></section>;
  }

  const cards = [
    ["Hackathons", stats.hackathons], ["Participants", stats.registrations], ["Problem statements", stats.problems],
    ["Teams", stats.teams], ["Proposals", stats.projects],
  ] as const;

  return (
    <section className="py-16 sm:py-20">
      <Container>
        <div className="flex flex-wrap items-end justify-between gap-5">
          <div><div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Organizer workspace</div><h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Run the hackathon.</h1><p className="mt-3 text-slate-600">Publish problems, monitor rosters and proposals, and answer participant questions.</p></div>
          <Button href={djangoAdminUrl} variant="secondary" size="sm" target="_blank" rel="noreferrer">Open full admin</Button>
        </div>
        {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}
        <div className="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-5">{cards.map(([label, value]) => <div key={label} className="card"><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</p><p className="mt-3 font-display text-4xl font-bold text-slate-900">{loading ? "..." : value}</p></div>)}</div>

        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          <div className="card"><h2 className="font-display text-xl font-semibold text-slate-900">Publish challenges</h2><p className="mt-3 text-sm leading-6 text-slate-600">Create problem statements with category, difficulty, brief, and expected deliverables.</p><Button href={`${djangoAdminUrl}hackathons/problemstatement/`} className="mt-5" size="sm" target="_blank" rel="noreferrer">Manage problems</Button></div>
          <div className="card"><h2 className="font-display text-xl font-semibold text-slate-900">Review proposals</h2><p className="mt-3 text-sm leading-6 text-slate-600">Inspect project files, intro videos, source links, and submission status.</p><Button href={`${djangoAdminUrl}projects/project/`} className="mt-5" size="sm" target="_blank" rel="noreferrer">Manage proposals</Button></div>
          <div className="card"><h2 className="font-display text-xl font-semibold text-slate-900">Manage registrations</h2><p className="mt-3 text-sm leading-6 text-slate-600">Review participant roles, team preferences, districts, and attendance plans.</p><Button href={`${djangoAdminUrl}hackathons/participantenrollment/`} className="mt-5" size="sm" target="_blank" rel="noreferrer">Manage registrations</Button></div>
        </div>

        <div className="mt-12">
          <div className="flex items-end justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Participant contact</p><h2 className="mt-2 font-display text-3xl font-semibold text-slate-900">Questions and proposal help</h2></div><span className="text-sm text-slate-500">{inquiriesLoading ? "Loading..." : `${inquiries.filter((item) => item.status === "open").length} open`}</span></div>
          <div className="mt-6 grid gap-5 lg:grid-cols-2">
            {!inquiriesLoading && inquiries.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-sm text-slate-600">No participant inquiries yet.</div> : null}
            {inquiries.map((inquiry) => <InquiryReview key={inquiry.id} inquiry={inquiry} onSaved={refetch} />)}
          </div>
        </div>
      </Container>
    </section>
  );
}
