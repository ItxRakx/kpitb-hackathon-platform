import { FormEvent, useCallback, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useHackathons, type Hackathon } from "@/hooks/useHackathons";
import { useProblems } from "@/hooks/useProblems";
import { useTeams, type Team } from "@/hooks/useTeams";
import { ApiError, api } from "@/lib/api";

function errorMessage(error: unknown): string {
  if (error instanceof ApiError && typeof error.data === "object" && error.data !== null) {
    const data = error.data as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    const first = Object.values(data).flat().find((value) => typeof value === "string");
    if (typeof first === "string") return first;
  }
  return "We could not complete that team action. Please try again.";
}

function TeamWorkspace({ team, hackathon }: { team: Team; hackathon?: Hackathon }) {
  const [detail, setDetail] = useState<Team>(team);
  const [inviteEmail, setInviteEmail] = useState("");
  const [working, setWorking] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const data = await api.get<Team>(`/teams/${team.id}/`);
    setDetail(data);
  }, [team.id]);

  useEffect(() => { void refresh(); }, [refresh]);

  async function run(action: string, request: () => Promise<unknown>, success: string) {
    setWorking(action);
    setError("");
    setMessage("");
    try {
      await request();
      await refresh();
      setMessage(success);
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setWorking("");
    }
  }

  async function sendInvite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await run("invite", () => api.post("/teams/invites/", { team: detail.id, email: inviteEmail.trim() }), "Invitation saved. The participant can join with their account.");
    setInviteEmail("");
  }

  const seatsLeft = Math.max(0, detail.max_members - detail.member_count);

  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            {detail.is_leader ? <span className="pill bg-brand-50 text-brand-700">Team lead</span> : <span className="pill bg-slate-100 text-slate-600">Member</span>}
            {detail.is_registered ? <span className="pill bg-emerald-50 text-emerald-700">Registered</span> : null}
            {detail.is_roster_locked ? <span className="pill bg-amber-50 text-amber-700">Roster locked</span> : null}
          </div>
          <h2 className="mt-3 font-display text-2xl font-bold text-slate-900">{detail.name}</h2>
          <p className="mt-1 text-sm text-slate-500">{detail.hackathon_title}</p>
          {detail.problem_statement_title ? <p className="mt-3 text-sm font-medium text-slate-700">Challenge: {detail.problem_statement_title}</p> : null}
        </div>
        <div className="text-right">
          <p className="font-display text-2xl font-bold text-slate-900">{detail.member_count}/{detail.max_members}</p>
          <p className="text-xs text-slate-500">team seats</p>
        </div>
      </div>

      <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100" aria-label={`${detail.member_count} of ${detail.max_members} team seats filled`}>
        <div className="h-full rounded-full bg-brand-600" style={{ width: `${Math.min(100, (detail.member_count / detail.max_members) * 100)}%` }} />
      </div>

      <div className="mt-6 divide-y divide-slate-100 rounded-2xl border border-slate-200">
        {(detail.memberships || []).map((membership) => (
          <div key={membership.id} className="flex flex-wrap items-center justify-between gap-3 px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">{`${membership.user.first_name} ${membership.user.last_name}`.trim() || membership.user.email}</p>
              <p className="text-xs text-slate-500">{membership.user.email}</p>
            </div>
            <div className="flex items-center gap-2">
              {membership.is_leader ? <span className="pill bg-brand-50 text-brand-700">Lead</span> : <span className="pill bg-slate-100 text-slate-600">Member</span>}
              {detail.is_leader && !membership.is_leader && !detail.is_roster_locked ? (
                <button type="button" className="text-xs font-semibold text-red-600 hover:underline" disabled={!!working} onClick={() => void run(`remove-${membership.user.id}`, () => api.post(`/teams/${detail.id}/members/${membership.user.id}/remove/`), "Member removed from the roster.")}>Remove</button>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      {error ? <div role="alert" className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      {message ? <div role="status" className="mt-5 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">{message}</div> : null}

      {detail.is_leader && !detail.is_roster_locked && seatsLeft > 0 ? (
        <form className="mt-6 flex flex-col gap-3 sm:flex-row" onSubmit={sendInvite}>
          <label className="sr-only" htmlFor={`invite-${detail.id}`}>Participant email</label>
          <input id={`invite-${detail.id}`} required type="email" value={inviteEmail} onChange={(event) => setInviteEmail(event.target.value)} className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder={`Invite by email - ${seatsLeft} seat${seatsLeft === 1 ? "" : "s"} left`} />
          <Button type="submit" size="sm" disabled={!!working}>{working === "invite" ? "Sending..." : "Invite member"}</Button>
        </form>
      ) : null}

      <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-slate-100 pt-5">
        {!detail.is_roster_locked && detail.invite_code ? (
          <Button type="button" variant="secondary" size="sm" onClick={() => void navigator.clipboard.writeText(detail.invite_code)}>Copy code {detail.invite_code}</Button>
        ) : null}
        {detail.is_leader && !detail.is_roster_locked ? (
          <Button type="button" size="sm" disabled={!!working} onClick={() => void run("lock", () => api.post(`/teams/${detail.id}/lock-roster/`), "Roster locked. You can now register the team.")}>{working === "lock" ? "Locking..." : "Lock roster"}</Button>
        ) : null}
        {detail.is_leader && detail.is_roster_locked && !detail.is_registered && hackathon ? (
          <Button type="button" size="sm" disabled={!!working} onClick={() => void run("register", () => api.post(`/hackathons/${hackathon.slug}/register-team/`, { team_id: detail.id }), "Team registered successfully.")}>{working === "register" ? "Registering..." : "Register for hackathon"}</Button>
        ) : null}
        {detail.is_leader && detail.is_roster_locked && !detail.is_registered ? (
          <Button type="button" variant="ghost" size="sm" disabled={!!working} onClick={() => void run("unlock", () => api.post(`/teams/${detail.id}/unlock-roster/`), "Roster reopened for changes.")}>Reopen roster</Button>
        ) : null}
        {detail.is_registered ? <Button to="/project" size="sm">Open submission</Button> : null}
      </div>
    </article>
  );
}

export default function TeamPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { hackathons, loading: hackathonsLoading } = useHackathons();
  const { teams, loading: teamsLoading } = useTeams(true);
  const [name, setName] = useState("");
  const [tagline, setTagline] = useState("");
  const [hackathonId, setHackathonId] = useState(() => searchParams.get("hackathon") || "");
  const [problemId, setProblemId] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const { problems, loading: problemsLoading } = useProblems(hackathonId || undefined);

  async function createTeam(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true); setError(""); setMessage("");
    try {
      await api.post<Team>("/teams/", {
        name: name.trim(), tagline: tagline.trim(), hackathon: Number(hackathonId),
        problem_statement: Number(problemId),
      });
      window.location.reload();
    } catch (requestError) {
      setError(errorMessage(requestError));
      setWorking(false);
    }
  }

  async function joinTeam(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true); setError(""); setMessage("");
    try {
      await api.post("/teams/join-by-code/", { invite_code: inviteCode.trim() });
      window.location.reload();
    } catch (requestError) {
      setError(errorMessage(requestError));
      setWorking(false);
    }
  }

  return (
    <section className="py-16 sm:py-20">
      <Container>
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate("/dashboard")} className="!px-0">Back to dashboard</Button>
        <div className="mt-6 max-w-3xl">
          <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Team workspace</div>
          <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Build a team of up to six.</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">One participant becomes the lead, chooses an official problem, and invites the rest of the team. The lead locks the final roster before registration.</p>
        </div>

        {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}
        {message ? <div role="status" className="mt-8 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">{message}</div> : null}

        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          <form className="card" onSubmit={createTeam}>
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Become a team lead</p>
            <h2 className="mt-2 font-display text-2xl font-semibold text-slate-900">Create a team</h2>
            <label className="mt-6 block text-sm font-semibold text-slate-700" htmlFor="team-name">Team name</label>
            <input id="team-name" required value={name} onChange={(event) => setName(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="e.g. Frontier Labs" />
            <label className="mt-4 block text-sm font-semibold text-slate-700" htmlFor="team-tagline">Team focus <span className="font-normal text-slate-400">(optional)</span></label>
            <input id="team-tagline" value={tagline} onChange={(event) => setTagline(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="What strengths are you bringing?" />
            <label className="mt-4 block text-sm font-semibold text-slate-700" htmlFor="team-hackathon">Hackathon</label>
            <select id="team-hackathon" required value={hackathonId} onChange={(event) => { setHackathonId(event.target.value); setProblemId(""); }} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm" disabled={hackathonsLoading}>
              <option value="">{hackathonsLoading ? "Loading hackathons..." : "Choose a hackathon"}</option>
              {hackathons.filter((hackathon) => hackathon.is_registration_open).map((hackathon) => <option key={hackathon.id} value={hackathon.id}>{hackathon.title}</option>)}
            </select>
            <label className="mt-4 block text-sm font-semibold text-slate-700" htmlFor="team-problem">Official problem statement</label>
            <select id="team-problem" required value={problemId} onChange={(event) => setProblemId(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm" disabled={!hackathonId || problemsLoading}>
              <option value="">{problemsLoading && hackathonId ? "Loading problems..." : "Choose the problem your team will solve"}</option>
              {problems.map((problem) => <option key={problem.id} value={problem.id}>{problem.category} - {problem.title}</option>)}
            </select>
            <Button type="submit" className="mt-6" disabled={working || !problemId}>{working ? "Creating..." : "Create team as lead"}</Button>
          </form>

          <form className="card" onSubmit={joinTeam}>
            <p className="text-xs font-semibold uppercase tracking-wider text-brand-600">Already invited?</p>
            <h2 className="mt-2 font-display text-2xl font-semibold text-slate-900">Join your team</h2>
            <p className="mt-6 text-sm leading-6 text-slate-600">Ask the team lead for the eight-character invite code. You can only join one team in the same hackathon.</p>
            <label className="mt-6 block text-sm font-semibold text-slate-700" htmlFor="invite-code">Invite code</label>
            <input id="invite-code" required value={inviteCode} onChange={(event) => setInviteCode(event.target.value.toUpperCase())} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 font-mono text-sm uppercase tracking-[0.2em]" placeholder="AB12CD34" maxLength={16} />
            <Button type="submit" variant="secondary" className="mt-6" disabled={working}>{working ? "Joining..." : "Join team"}</Button>
          </form>
        </div>

        <div className="mt-12">
          <div className="flex items-end justify-between gap-4">
            <div><p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Your teams</p><h2 className="mt-2 font-display text-2xl font-semibold text-slate-900">Roster and registration</h2></div>
            <span className="text-sm text-slate-500">{teamsLoading ? "Loading..." : `${teams.length} team${teams.length === 1 ? "" : "s"}`}</span>
          </div>
          <div className="mt-5 grid gap-5 xl:grid-cols-2">
            {!teamsLoading && teams.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-sm text-slate-600">You are not in a team yet. Create one as lead or join with an invite code.</div> : null}
            {teams.map((team) => <TeamWorkspace key={team.id} team={team} hackathon={hackathons.find((item) => item.id === team.hackathon)} />)}
          </div>
        </div>
      </Container>
    </section>
  );
}
