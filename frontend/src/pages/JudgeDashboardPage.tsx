import { useEffect, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useHackathons, type Hackathon } from "@/hooks/useHackathons";
import { ApiError, api } from "@/lib/api";

type JudgeProject = { id: number; title: string; slug: string; team_name: string; hackathon_title: string; description: string; short_description: string; track: string | null; repo_url: string | null; demo_url: string | null; attachments: Array<{ id: number; display_name: string; file_url: string }>; };
type Criterion = { id: number; name: string; max_score: number; weight: number; description: string };

export default function JudgeDashboardPage() {
  const { hackathons, loading: hackathonsLoading } = useHackathons("current");
  const [selectedSlug, setSelectedSlug] = useState("");
  const [projects, setProjects] = useState<JudgeProject[]>([]);
  const [criteria, setCriteria] = useState<Criterion[]>([]);
  const [scores, setScores] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!selectedSlug && hackathons[0]) setSelectedSlug(hackathons[0].slug);
  }, [hackathons, selectedSlug]);

  useEffect(() => {
    if (!selectedSlug) return;
    let active = true;
    setLoading(true);
    setError("");
    Promise.all([
      api.get<JudgeProject[]>(`/judging/hackathons/${selectedSlug}/projects/`),
      api.get<{ results?: Criterion[] } | Criterion[]>(`/hackathons/criteria/?hackathon=${selectedSlug}`),
    ]).then(([projectData, criterionData]) => {
      if (!active) return;
      setProjects(projectData);
      setCriteria(Array.isArray(criterionData) ? criterionData : criterionData.results || []);
    }).catch((requestError: ApiError | Error) => {
      if (active) setError(requestError instanceof ApiError && typeof requestError.data === "object" && requestError.data !== null ? String((requestError.data as { detail?: string }).detail || "Unable to load assigned projects.") : "Unable to load assigned projects.");
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [selectedSlug]);

  async function saveScore(projectId: number, criterion: Criterion) {
    const value = Number(scores[`${projectId}-${criterion.id}`]);
    if (!Number.isFinite(value)) return;
    setMessage("");
    setError("");
    try {
      await api.post("/judging/scores/", { project: projectId, criterion: criterion.id, value });
      setMessage("Score saved.");
    } catch {
      setError("Score could not be saved. Confirm that the project is assigned to you.");
    }
  }

  return (
    <section className="py-16 sm:py-20"><Container size="md"><div className="flex flex-wrap items-end justify-between gap-5"><div><div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Judge workspace</div><h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Review assigned projects.</h1><p className="mt-3 text-slate-600">Scores are saved against the criteria configured for each hackathon.</p></div><select value={selectedSlug} onChange={(event) => setSelectedSlug(event.target.value)} disabled={hackathonsLoading} className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="">{hackathonsLoading ? "Loading hackathons..." : "Choose hackathon"}</option>{hackathons.map((hackathon: Hackathon) => <option key={hackathon.id} value={hackathon.slug}>{hackathon.title}</option>)}</select></div>
      {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}{message ? <div role="status" className="mt-8 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">{message}</div> : null}
      <div className="mt-10 space-y-6">{loading ? <div className="rounded-2xl bg-slate-50 p-8 text-center text-sm text-slate-500">Loading assigned projects...</div> : null}{!loading && selectedSlug && projects.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-600">No submitted projects are assigned to you yet.</div> : null}{projects.map((project) => <article key={project.id} className="card"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="pill bg-brand-50 text-brand-700">{project.track || "Open track"}</div><h2 className="mt-3 font-display text-2xl font-bold text-slate-900">{project.title}</h2><p className="mt-1 text-sm text-slate-500">{project.team_name} · {project.hackathon_title}</p></div><div className="flex gap-2">{project.repo_url ? <Button href={project.repo_url} variant="secondary" size="sm">Repository</Button> : null}{project.demo_url ? <Button href={project.demo_url} size="sm">Live demo</Button> : null}</div></div><p className="mt-5 text-sm leading-6 text-slate-600">{project.description || project.short_description}</p>{project.attachments.length > 0 ? <div className="mt-5 flex flex-wrap gap-2">{project.attachments.map((attachment) => <a key={attachment.id} href={attachment.file_url} target="_blank" rel="noreferrer" className="pill bg-slate-100 text-slate-600 hover:bg-slate-200">{attachment.display_name}</a>)}</div> : null}<div className="mt-6 border-t border-slate-100 pt-5"><h3 className="font-display text-lg font-semibold text-slate-900">Evaluation</h3><div className="mt-4 grid gap-3 md:grid-cols-2">{criteria.map((criterion) => <div key={criterion.id} className="rounded-xl border border-slate-200 p-4"><div className="flex justify-between gap-3"><label className="text-sm font-semibold text-slate-700" htmlFor={`score-${project.id}-${criterion.id}`}>{criterion.name}</label><span className="text-xs text-slate-500">/{criterion.max_score}</span></div><div className="mt-3 flex gap-2"><input id={`score-${project.id}-${criterion.id}`} type="number" min="0" max={criterion.max_score} value={scores[`${project.id}-${criterion.id}`] || ""} onChange={(event) => setScores((current) => ({ ...current, [`${project.id}-${criterion.id}`]: event.target.value }))} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" /><Button type="button" size="sm" onClick={() => void saveScore(project.id, criterion)}>Save</Button></div></div>)}</div></div></article>)}</div></Container></section>
  );
}
