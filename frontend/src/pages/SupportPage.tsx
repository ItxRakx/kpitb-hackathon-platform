import { FormEvent, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useHackathons } from "@/hooks/useHackathons";
import { useInquiries } from "@/hooks/useInquiries";
import { useProjects } from "@/hooks/useProjects";
import { ApiError, api } from "@/lib/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-PK", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function SupportPage() {
  const { inquiries, loading, refetch } = useInquiries();
  const { projects } = useProjects(true);
  const { hackathons } = useHackathons();
  const [projectId, setProjectId] = useState("");
  const [hackathonId, setHackathonId] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [working, setWorking] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true); setNotice(""); setError("");
    try {
      await api.post("/projects/inquiries/", {
        project: projectId ? Number(projectId) : null,
        hackathon: hackathonId ? Number(hackathonId) : null,
        subject: subject.trim(),
        message: message.trim(),
      });
      setProjectId(""); setHackathonId(""); setSubject(""); setMessage("");
      setNotice("Your question has been sent to the organizers.");
      await refetch();
    } catch (requestError) {
      setError(requestError instanceof ApiError ? "Please check your message and try again." : "Your message could not be sent.");
    } finally {
      setWorking(false);
    }
  }

  return (
    <section className="py-16 sm:py-20">
      <Container size="md">
        <div className="max-w-3xl">
          <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Organizer help desk</div>
          <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Ask about your proposal.</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">Send a question about registration, your selected problem, team, or submission. Organizer replies remain visible here.</p>
        </div>

        <div className="mt-10 grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
          <form onSubmit={submit} className="card h-fit space-y-5">
            {error ? <div role="alert" className="rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
            {notice ? <div role="status" className="rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">{notice}</div> : null}
            <label className="block text-sm font-semibold text-slate-700">Related project <span className="font-normal text-slate-400">(optional)</span>
              <select value={projectId} onChange={(event) => setProjectId(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm">
                <option value="">General question</option>
                {projects.map((project) => <option key={project.id} value={project.id}>{project.title}</option>)}
              </select>
            </label>
            {!projectId ? <label className="block text-sm font-semibold text-slate-700">Hackathon <span className="font-normal text-slate-400">(optional)</span>
              <select value={hackathonId} onChange={(event) => setHackathonId(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm">
                <option value="">Platform support</option>
                {hackathons.map((hackathon) => <option key={hackathon.id} value={hackathon.id}>{hackathon.title}</option>)}
              </select>
            </label> : null}
            <label className="block text-sm font-semibold text-slate-700">Subject
              <input required maxLength={180} value={subject} onChange={(event) => setSubject(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="What do you need help with?" />
            </label>
            <label className="block text-sm font-semibold text-slate-700">Message
              <textarea required rows={6} value={message} onChange={(event) => setMessage(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="Include the context the organizers need to answer." />
            </label>
            <Button type="submit" disabled={working}>{working ? "Sending..." : "Send to organizers"}</Button>
          </form>

          <div>
            <div className="flex items-center justify-between gap-4"><h2 className="font-display text-2xl font-semibold text-slate-900">Your questions</h2><span className="text-sm text-slate-500">{loading ? "Loading..." : inquiries.length}</span></div>
            <div className="mt-5 space-y-4">
              {!loading && inquiries.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-sm text-slate-600">You have not contacted the organizers yet.</div> : null}
              {inquiries.map((inquiry) => (
                <article key={inquiry.id} className="rounded-2xl border border-slate-200 bg-white p-5">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div><h3 className="font-semibold text-slate-900">{inquiry.subject}</h3><p className="mt-1 text-xs text-slate-400">{inquiry.project_title || inquiry.hackathon_title || "Platform support"} - {formatDate(inquiry.created_at)}</p></div>
                    <span className={`pill capitalize ${inquiry.status === "answered" ? "bg-emerald-50 text-emerald-700" : inquiry.status === "closed" ? "bg-slate-100 text-slate-600" : "bg-amber-50 text-amber-700"}`}>{inquiry.status}</span>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-600">{inquiry.message}</p>
                  {inquiry.admin_response ? <div className="mt-5 rounded-xl bg-brand-50 p-4"><p className="text-xs font-bold uppercase tracking-wider text-brand-700">Organizer response</p><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{inquiry.admin_response}</p></div> : null}
                </article>
              ))}
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
