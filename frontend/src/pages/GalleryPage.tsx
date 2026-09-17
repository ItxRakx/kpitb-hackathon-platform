import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useProjects } from "@/hooks/useProjects";
import { Link } from "react-router-dom";

export default function GalleryPage() {
  const { projects, loading, error } = useProjects();

  return (
    <section className="py-20">
      <Container size="md">
        <div className="text-center">
        <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Project Gallery
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-base text-slate-600 sm:text-lg">
          Explore public submissions from builders across the KPITB community.
        </p>
        </div>

        <div className="mt-10">
          {loading && <div className="rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">Loading projects...</div>}
          {error && <div role="alert" className="rounded-2xl bg-red-50 p-8 text-center text-sm text-red-700">Projects are temporarily unavailable. Please try again shortly.</div>}
          {!loading && !error && projects.length === 0 && <div className="rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">No public projects have been published yet.</div>}
          {!loading && !error && projects.length > 0 && (
            <div className="grid gap-5 md:grid-cols-2">
              {projects.map((project) => (
                <Link key={project.id} to={`/projects/${project.slug}`} className="card block">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="pill bg-brand-50 text-brand-700">{project.track || "Open track"}</div>
                      <h2 className="mt-4 font-display text-2xl font-bold text-slate-900">{project.title}</h2>
                    </div>
                    <span className="text-xs font-semibold text-slate-400">{project.build_mode}</span>
                  </div>
                  <p className="mt-3 text-sm text-slate-600">{project.short_description || project.tagline || "A project built by the KPITB community."}</p>
                  <dl className="mt-6 grid grid-cols-2 gap-4 border-t border-slate-100 pt-5 text-sm">
                    <div><dt className="text-slate-500">Team</dt><dd className="mt-1 font-semibold text-slate-900">{project.team_name}</dd></div>
                    <div><dt className="text-slate-500">Hackathon</dt><dd className="mt-1 font-semibold text-slate-900">{project.hackathon_title}</dd></div>
                  </dl>
                  {project.technologies.length > 0 && <div className="mt-5 flex flex-wrap gap-2">{project.technologies.map((technology) => <span key={technology} className="pill bg-slate-100 text-slate-600">{technology}</span>)}</div>}
                </Link>
              ))}
            </div>
          )}
        </div>
        <div className="mt-10 text-center"><Button to="/" variant="secondary">← Back to Home</Button></div>
      </Container>
    </section>
  );
}
