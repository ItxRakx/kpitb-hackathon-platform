import { useNavigate } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useUser } from "@/hooks/useAuth";
import { useHackathons } from "@/hooks/useHackathons";
import { useProjects } from "@/hooks/useProjects";
import { useTeams } from "@/hooks/useTeams";
import { clearTokens } from "@/lib/auth";
import { useMyEnrollments } from "@/hooks/useEnrollment";

export default function DashboardPage() {
  const navigate = useNavigate();
  const { loading, user, error } = useUser();
  const { hackathons, loading: hackathonsLoading } = useHackathons();
  const { teams, loading: teamsLoading } = useTeams(true);
  const { projects, loading: projectsLoading } = useProjects(true);
  const { enrollments } = useMyEnrollments();
  const openHackathons = hackathons.filter((hackathon) => hackathon.is_registration_open);

  function handleLogout() {
    clearTokens();
    navigate("/", { replace: true });
  }

  return (
    <section className="py-16 sm:py-20">
      <Container>
        <div className="flex flex-wrap items-start justify-between gap-5">
          <div>
            <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Participant dashboard</div>
            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              {loading ? "Loading your workspace..." : `Welcome${user?.first_name ? `, ${user.first_name}` : " back"}.`}
            </h1>
            <p className="mt-4 max-w-2xl text-base text-slate-600">
              Complete each step in order: profile, official problem, team roster, registration, then proposal.
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={handleLogout}>Sign out</Button>
        </div>

        {error ? (
          <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            We could not load your profile. Please sign in again.
          </div>
        ) : (
          <div className="mt-10 space-y-8">
            <div className="grid gap-5 md:grid-cols-3">
              <div className="card">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Current events</p>
                <p className="mt-3 font-display text-3xl font-bold text-slate-900">
                  {hackathonsLoading ? "..." : openHackathons.length}
                </p>
                <p className="mt-2 text-sm text-slate-600">Hackathons currently accepting builders.</p>
                <Button to="/hackathons" variant="ghost" size="sm" className="mt-5 !px-0">Browse events</Button>
              </div>
              <div className="card">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Your teams</p>
                <p className="mt-3 font-display text-3xl font-bold text-slate-900">
                  {teamsLoading ? "..." : teams.length}
                </p>
                <p className="mt-2 text-sm text-slate-600">Teams you belong to across hackathons.</p>
                <Button to="/team" variant="ghost" size="sm" className="mt-5 !px-0">Manage teams</Button>
              </div>
              <div className="card">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Your projects</p>
                <p className="mt-3 font-display text-3xl font-bold text-slate-900">
                  {projectsLoading ? "..." : projects.length}
                </p>
                <p className="mt-2 text-sm text-slate-600">Public and private projects linked to your teams.</p>
                <Button to="/gallery" variant="ghost" size="sm" className="mt-5 !px-0">Explore gallery</Button>
              </div>
            </div>

            <div className="grid gap-3 rounded-3xl border border-slate-200 bg-slate-950 p-5 text-white sm:grid-cols-5 sm:p-6">
              {[
                ["01", "Profile", user?.profile?.is_complete, "/profile"],
                ["02", "Event", enrollments.length > 0, "/hackathons"],
                ["03", "Team", teams.length > 0, "/team"],
                ["04", "Roster", teams.some((team) => team.is_registered), "/team"],
                ["05", "Proposal", projects.length > 0, "/project"],
              ].map(([number, label, done, href]) => (
                <button key={String(label)} type="button" onClick={() => navigate(String(href))} className="flex items-center gap-3 rounded-2xl bg-white/5 p-3 text-left transition hover:bg-white/10 sm:block">
                  <span className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${done ? "bg-emerald-400 text-emerald-950" : "bg-white/10 text-white"}`}>{done ? "✓" : number}</span>
                  <span className="mt-0 text-sm font-semibold sm:mt-3 sm:block">{String(label)}</span>
                </button>
              ))}
            </div>

            <div className="flex flex-wrap gap-3">
              <Button to="/project" size="sm">Open proposal workspace</Button>
              <Button to="/profile" variant="secondary" size="sm">Edit profile</Button>
              <Button to="/support" variant="secondary" size="sm">Ask organizers</Button>
              <Button to="/notifications" variant="secondary" size="sm">Open notifications</Button>
            </div>

            <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="card">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Active workspace</p>
                    <h2 className="mt-2 font-display text-2xl font-semibold text-slate-900">Keep building</h2>
                  </div>
                  <Button to="/hackathons" size="sm">View hackathons</Button>
                </div>
                {hackathonsLoading ? (
                  <p className="mt-8 text-sm text-slate-500">Loading current events...</p>
                ) : openHackathons.length === 0 ? (
                  <p className="mt-8 text-sm text-slate-500">There are no active hackathons right now. Check back soon.</p>
                ) : (
                  <div className="mt-6 space-y-3">
                    {openHackathons.slice(0, 3).map((hackathon) => (
                      <div key={hackathon.id} className="rounded-xl bg-slate-50 p-4 ring-1 ring-inset ring-slate-200">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div>
                            <h3 className="font-semibold text-slate-900">{hackathon.title}</h3>
                            <p className="mt-1 text-sm text-slate-500">Teams of {hackathon.team_min_size} to {hackathon.team_max_size}</p>
                          </div>
                          <span className="pill bg-emerald-50 text-emerald-700">Registration open</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="card">
                <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Team snapshot</p>
                <h2 className="mt-2 font-display text-2xl font-semibold text-slate-900">Your crew</h2>
                {teamsLoading ? (
                  <p className="mt-8 text-sm text-slate-500">Loading your teams...</p>
                ) : teams.length === 0 ? (
                  <div className="mt-6 rounded-xl border border-dashed border-slate-300 p-5">
                    <p className="text-sm leading-6 text-slate-600">You have not joined a team yet. Find an event and start forming your roster.</p>
                    <Button to="/team" variant="secondary" size="sm" className="mt-5">Create or join a team</Button>
                  </div>
                ) : (
                  <div className="mt-6 space-y-3">
                    {teams.slice(0, 3).map((team) => (
                      <div key={team.id} className="rounded-xl border border-slate-200 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <h3 className="font-semibold text-slate-900">{team.name}</h3>
                          <span className="text-xs font-medium text-slate-500">{team.member_count} member{team.member_count === 1 ? "" : "s"}</span>
                        </div>
                        <p className="mt-1 text-sm text-slate-500">{team.hackathon_title}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </Container>
    </section>
  );
}
