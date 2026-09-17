import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useProject } from "@/hooks/useProject";
import { ApiError, api } from "@/lib/api";

export default function ProjectDetailPage() {
  const { slug = "" } = useParams();
  const location = useLocation();
  const { project, loading, error } = useProject(slug);
  const [working, setWorking] = useState(false);
  const [actionError, setActionError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  async function submitProject() {
    if (!project) return;
    setWorking(true); setActionError("");
    try {
      await api.post(`/projects/${project.slug}/submit/`, {});
      setSubmitted(true);
      window.location.reload();
    } catch (requestError) {
      if (requestError instanceof ApiError && typeof requestError.data === "object" && requestError.data) {
        setActionError((requestError.data as { detail?: string }).detail || "The project could not be submitted.");
      } else setActionError("The project could not be submitted.");
      setWorking(false);
    }
  }

  if (loading) return <section className="py-20"><Container size="md"><div className="rounded-2xl border border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">Loading project...</div></Container></section>;
  if (error || !project) return <section className="py-20"><Container size="md" className="text-center"><h1 className="font-display text-3xl font-bold text-slate-900">Project not found</h1><p className="mt-3 text-slate-600">This project may be private or no longer available.</p><div className="mt-8"><Button to="/gallery">Back to gallery</Button></div></Container></section>;

  const videoAttachments = project.attachments.filter((item) => item.attachment_type === "demo_video");
  const otherAttachments = project.attachments.filter((item) => item.attachment_type !== "demo_video");
  const isDraft = project.status === "draft" && !submitted;

  return (
    <section className="py-16 sm:py-20">
      <Container size="md">
        <Link to={project.is_public ? "/gallery" : "/dashboard"} className="text-sm font-semibold text-brand-600 hover:underline">Back to {project.is_public ? "gallery" : "dashboard"}</Link>
        {location.state?.created ? <div role="status" className="mt-6 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">Proposal draft saved. Review it below, then submit it for organizer review.</div> : null}
        {actionError ? <div role="alert" className="mt-6 rounded-xl bg-red-50 p-4 text-sm text-red-700">{actionError}</div> : null}
        <div className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sm:p-10">
          <div className="flex flex-wrap items-center gap-2">
            <span className="pill bg-brand-50 text-brand-700">{project.problem_statement_title || project.track || "Open challenge"}</span>
            <span className={`pill capitalize ${isDraft ? "bg-amber-50 text-amber-700" : "bg-emerald-50 text-emerald-700"}`}>{project.status.replace("_", " ")}</span>
          </div>
          <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">{project.title}</h1>
          <p className="mt-4 text-lg text-slate-600">{project.tagline || project.short_description}</p>
          <div className="mt-6 flex flex-wrap gap-2">{project.technologies.map((technology) => <span key={technology} className="pill bg-slate-100 text-slate-600">{technology}</span>)}</div>

          <div className="mt-10 grid gap-8 border-t border-slate-100 pt-8 md:grid-cols-[1fr_220px]">
            <div><h2 className="font-display text-xl font-semibold text-slate-900">Proposal</h2><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{project.description || project.short_description}</p></div>
            <dl className="space-y-4 text-sm"><div><dt className="text-slate-500">Built by</dt><dd className="mt-1 font-semibold text-slate-900">{project.team_name}</dd></div><div><dt className="text-slate-500">Hackathon</dt><dd className="mt-1 font-semibold text-slate-900">{project.hackathon_title}</dd></div><div><dt className="text-slate-500">Build mode</dt><dd className="mt-1 font-semibold capitalize text-slate-900">{project.build_mode}</dd></div></dl>
          </div>

          {(project.demo_video_url || videoAttachments.length > 0) ? <div className="mt-8 border-t border-slate-100 pt-8"><h2 className="font-display text-xl font-semibold text-slate-900">Team intro</h2>{videoAttachments.map((attachment) => <video key={attachment.id} controls preload="metadata" className="mt-4 aspect-video w-full rounded-2xl bg-slate-950"><source src={attachment.file_url} /></video>)}{project.demo_video_url ? <Button href={project.demo_video_url} variant="secondary" className="mt-4" target="_blank" rel="noreferrer">Open hosted intro video</Button> : null}</div> : null}

          {otherAttachments.length > 0 ? <div className="mt-8 border-t border-slate-100 pt-8"><h2 className="font-display text-xl font-semibold text-slate-900">Proposal files</h2><div className="mt-4 grid gap-3 sm:grid-cols-2">{otherAttachments.map((attachment) => <a key={attachment.id} href={attachment.file_url} target="_blank" rel="noreferrer" className="rounded-xl border border-slate-200 p-4 text-sm font-semibold text-slate-800 hover:border-brand-300 hover:bg-brand-50"><span className="block text-xs font-medium uppercase tracking-wider text-slate-400">{attachment.attachment_type.replace("_", " ")}</span><span className="mt-1 block">{attachment.display_name}</span></a>)}</div></div> : null}

          <div className="mt-8 flex flex-wrap gap-3 border-t border-slate-100 pt-8">
            {project.repo_url ? <Button href={project.repo_url} variant="secondary" target="_blank" rel="noreferrer">View source</Button> : null}
            {project.demo_url ? <Button href={project.demo_url} target="_blank" rel="noreferrer">Open live demo</Button> : null}
            {project.is_leader && isDraft ? <Button type="button" disabled={working} onClick={() => void submitProject()}>{working ? "Submitting..." : "Submit for organizer review"}</Button> : null}
            {project.is_leader ? <Button to="/support" variant="ghost">Ask organizers</Button> : null}
          </div>
          {project.is_leader && isDraft ? <p className="mt-3 text-xs text-slate-500">Submitting locks the proposal. An organizer can reopen it if changes are required.</p> : null}
        </div>
      </Container>
    </section>
  );
}
