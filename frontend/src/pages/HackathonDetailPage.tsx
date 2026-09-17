import { FormEvent, useState } from "react";
import { useParams } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useUser } from "@/hooks/useAuth";
import { useEnrollment } from "@/hooks/useEnrollment";
import { useHackathon } from "@/hooks/useHackathons";
import { useProblems } from "@/hooks/useProblems";
import { ApiError, api } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";

function formatDate(value: string, withTime = false) {
  return new Intl.DateTimeFormat("en-PK", withTime ? { dateStyle: "medium", timeStyle: "short" } : { dateStyle: "long" }).format(new Date(value));
}

function registrationError(error: unknown) {
  if (error instanceof ApiError && error.data && typeof error.data === "object") {
    const data = error.data as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    const first = Object.values(data).flat().find((value) => typeof value === "string");
    if (typeof first === "string") return first;
  }
  return "Registration could not be completed. Please review the form and try again.";
}

export default function HackathonDetailPage() {
  const { slug = "" } = useParams();
  const { hackathon, loading, error } = useHackathon(slug);
  const { problems } = useProblems(slug);
  const { user } = useUser();
  const { enrollment, loading: enrollmentLoading, refetch } = useEnrollment(slug);
  const [form, setForm] = useState({
    participationPreference: "need_team",
    primaryRole: "developer",
    experienceLevel: "intermediate",
    attendanceMode: "flexible",
    selectedProblem: "",
    motivation: "",
    agreedToRules: false,
  });
  const [working, setWorking] = useState(false);
  const [formError, setFormError] = useState("");

  function update(field: keyof typeof form, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function enroll(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true); setFormError("");
    try {
      await api.post(`/hackathons/${slug}/enrollment/`, {
        participation_preference: form.participationPreference,
        primary_role: form.primaryRole,
        experience_level: form.experienceLevel,
        attendance_mode: form.attendanceMode,
        selected_problem: form.selectedProblem ? Number(form.selectedProblem) : null,
        motivation: form.motivation.trim(),
        agreed_to_rules: form.agreedToRules,
      });
      await refetch();
    } catch (requestError) {
      setFormError(registrationError(requestError));
    } finally {
      setWorking(false);
    }
  }

  if (loading) return <section className="py-20"><Container><div className="rounded-3xl border border-slate-200 bg-slate-50 p-12 text-center text-sm text-slate-500">Loading event...</div></Container></section>;
  if (error || !hackathon) return <section className="py-20"><Container size="sm" className="text-center"><h1 className="font-display text-3xl font-bold text-slate-900">Hackathon not found</h1><Button to="/hackathons" className="mt-7">Browse hackathons</Button></Container></section>;

  const redirect = encodeURIComponent(`/hackathons/${hackathon.slug}`);
  const registered = !!enrollment && enrollment.status !== "cancelled";

  return (
    <>
      <section className="bg-slate-950 py-14 text-white sm:py-20">
        <Container>
          <div className="grid gap-10 lg:grid-cols-[1fr_360px] lg:items-start">
            <div className="max-w-4xl">
              <div className="flex flex-wrap items-center gap-3">
                <span className={`pill ${hackathon.is_registration_open ? "bg-emerald-400 text-emerald-950" : "bg-white/10 text-white"}`}>{hackathon.is_registration_open ? "Registration open" : hackathon.is_ongoing ? "Live now" : "Registration closed"}</span>
                <span className="text-sm font-medium text-slate-300">{hackathon.participant_count} registered participants</span>
              </div>
              <h1 className="mt-6 font-display text-4xl font-bold tracking-tight sm:text-6xl">{hackathon.title}</h1>
              <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-300">{hackathon.tagline || hackathon.description}</p>
              <dl className="mt-10 grid gap-5 border-t border-white/10 pt-7 sm:grid-cols-3">
                <div><dt className="text-xs font-bold uppercase tracking-wider text-slate-400">Build dates</dt><dd className="mt-2 text-sm font-semibold">{formatDate(hackathon.starts_at)} - {formatDate(hackathon.ends_at)}</dd></div>
                <div><dt className="text-xs font-bold uppercase tracking-wider text-slate-400">Registration closes</dt><dd className="mt-2 text-sm font-semibold">{formatDate(hackathon.registration_closes_at, true)}</dd></div>
                <div><dt className="text-xs font-bold uppercase tracking-wider text-slate-400">Team size</dt><dd className="mt-2 text-sm font-semibold">{hackathon.team_min_size}-{hackathon.team_max_size} participants</dd></div>
              </dl>
            </div>

            <aside id="register" className="rounded-3xl bg-white p-6 text-slate-900 shadow-2xl shadow-black/30">
              {registered ? (
                <div>
                  <span className="pill bg-emerald-50 text-emerald-700">Registration confirmed</span>
                  <h2 className="mt-4 font-display text-2xl font-bold">You are in.</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">Your individual place is registered. Every future team member must complete this step too.</p>
                  <dl className="mt-5 space-y-3 rounded-2xl bg-slate-50 p-4 text-sm"><div><dt className="text-slate-500">Role</dt><dd className="mt-1 font-semibold capitalize text-slate-900">{enrollment.primary_role.replace("_", " ")}</dd></div><div><dt className="text-slate-500">Team plan</dt><dd className="mt-1 font-semibold capitalize text-slate-900">{enrollment.participation_preference.replace(/_/g, " ")}</dd></div></dl>
                  <Button to={`/team?hackathon=${hackathon.id}`} className="mt-6 w-full">Create or join a team</Button>
                  <Button to="/dashboard" variant="ghost" className="mt-2 w-full">View my dashboard</Button>
                </div>
              ) : !hackathon.is_registration_open ? (
                <div><h2 className="font-display text-2xl font-bold">Registration is closed</h2><p className="mt-3 text-sm leading-6 text-slate-600">You can still review the event details and published challenges below.</p></div>
              ) : !isAuthenticated() ? (
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-brand-600">Join this event</p>
                  <h2 className="mt-2 font-display text-2xl font-bold">Register as a participant</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">Sign in or create an account first. You will return to this event to complete registration.</p>
                  <Button to={`/login?redirect=${redirect}`} className="mt-6 w-full">Sign in to register</Button>
                  <Button to={`/register?redirect=${redirect}`} variant="secondary" className="mt-3 w-full">Create participant account</Button>
                </div>
              ) : !user?.profile?.is_complete ? (
                <div>
                  <span className="pill bg-amber-50 text-amber-700">Profile required</span>
                  <h2 className="mt-4 font-display text-2xl font-bold">Complete your profile first</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">Add your district, institution, phone, and skills so organizers and team leads have enough information.</p>
                  <Button to="/profile" className="mt-6 w-full">Complete profile</Button>
                </div>
              ) : enrollmentLoading ? <p className="text-sm text-slate-500">Checking your registration...</p> : (
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-brand-600">Free registration</p>
                  <h2 className="mt-2 font-display text-2xl font-bold">Ready to take part?</h2>
                  <p className="mt-3 text-sm leading-6 text-slate-600">The form below takes about two minutes. No project upload is needed yet.</p>
                  <a href="#registration-form" className="btn-primary mt-6 w-full">Start registration</a>
                </div>
              )}
            </aside>
          </div>
        </Container>
      </section>

      <section className="py-14 sm:py-20">
        <Container>
          <div className="grid gap-12 lg:grid-cols-[minmax(0,1fr)_360px]">
            <div className="space-y-14">
              <section>
                <p className="text-xs font-bold uppercase tracking-wider text-brand-600">About the event</p>
                <h2 className="mt-3 font-display text-3xl font-bold text-slate-950">What you will build</h2>
                <p className="mt-5 whitespace-pre-wrap text-base leading-8 text-slate-600">{hackathon.description || "Work with participants from across Khyber Pakhtunkhwa to build a useful, testable solution for an official challenge."}</p>
                <div className="mt-7 grid gap-4 sm:grid-cols-3">{hackathon.tracks.map((track) => <div key={track} className="rounded-2xl border border-slate-200 bg-white p-4 text-sm font-semibold text-slate-800">{track}</div>)}</div>
              </section>

              <section>
                <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-wider text-brand-600">Official challenges</p><h2 className="mt-3 font-display text-3xl font-bold text-slate-950">Choose a direction</h2></div><Button to="/problems" variant="secondary" size="sm">View all problem details</Button></div>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">{problems.map((problem) => <article key={problem.id} className="rounded-2xl border border-slate-200 bg-white p-5"><div className="flex items-center justify-between gap-3"><span className="pill bg-brand-50 text-brand-700">{problem.category}</span><span className="text-xs font-semibold capitalize text-slate-400">{problem.difficulty}</span></div><h3 className="mt-4 font-display text-xl font-semibold text-slate-900">{problem.title}</h3><p className="mt-2 text-sm leading-6 text-slate-600">{problem.summary}</p></article>)}</div>
              </section>

              <section className="rounded-3xl bg-slate-50 p-6 sm:p-8">
                <p className="text-xs font-bold uppercase tracking-wider text-brand-600">Complete submission</p>
                <h2 className="mt-3 font-display text-3xl font-bold text-slate-950">What your team submits later</h2>
                <div className="mt-6 grid gap-4 sm:grid-cols-3">{[["01", "Working prototype", "A demo judges can open and use."], ["02", "Short video", "A clear product and impact walkthrough."], ["03", "Pitch deck", "Problem, solution, evidence, and next steps."]].map(([number, title, copy]) => <div key={number} className="rounded-2xl bg-white p-5"><span className="font-mono text-sm font-bold text-brand-600">{number}</span><h3 className="mt-3 font-semibold text-slate-900">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-600">{copy}</p></div>)}</div>
              </section>

              {(hackathon.rules || hackathon.prizes_text) ? <section className="grid gap-6 sm:grid-cols-2">{hackathon.rules ? <div><p className="text-xs font-bold uppercase tracking-wider text-brand-600">Rules</p><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{hackathon.rules}</p>{hackathon.rules_url ? <Button href={hackathon.rules_url} variant="secondary" size="sm" className="mt-4" target="_blank" rel="noreferrer">Open full rules</Button> : null}</div> : null}{hackathon.prizes_text ? <div><p className="text-xs font-bold uppercase tracking-wider text-brand-600">Prizes and support</p><p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{hackathon.prizes_text}</p></div> : null}</section> : null}
            </div>

            {isAuthenticated() && user?.profile?.is_complete && hackathon.is_registration_open && !registered && !enrollmentLoading ? (
              <form id="registration-form" onSubmit={enroll} className="h-fit scroll-mt-24 rounded-3xl border border-slate-200 bg-white p-6 shadow-soft lg:sticky lg:top-24">
                <p className="text-xs font-bold uppercase tracking-wider text-brand-600">Participant registration</p>
                <h2 className="mt-2 font-display text-2xl font-bold text-slate-950">Tell us how you will take part</h2>
                {formError ? <div role="alert" className="mt-5 rounded-xl bg-red-50 p-3 text-sm text-red-700">{formError}</div> : null}
                <div className="mt-6 space-y-5">
                  <label className="block text-sm font-semibold text-slate-700">Team plan<select value={form.participationPreference} onChange={(event) => update("participationPreference", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="need_team">Help me find a team</option><option value="create_team">I want to lead a team</option><option value="join_team">I already have a team</option><option value="solo">I plan to build solo</option></select></label>
                  <label className="block text-sm font-semibold text-slate-700">Primary role<select value={form.primaryRole} onChange={(event) => update("primaryRole", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="developer">Software developer</option><option value="data_ai">Data / AI</option><option value="designer">Designer / UX</option><option value="product">Product / business</option><option value="domain_expert">Domain expert</option><option value="student">Student / learner</option><option value="other">Other</option></select></label>
                  <label className="block text-sm font-semibold text-slate-700">Experience level<select value={form.experienceLevel} onChange={(event) => update("experienceLevel", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label>
                  <label className="block text-sm font-semibold text-slate-700">Attendance preference<select value={form.attendanceMode} onChange={(event) => update("attendanceMode", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="flexible">Either / flexible</option><option value="onsite">On-site</option><option value="online">Online</option></select></label>
                  <label className="block text-sm font-semibold text-slate-700">Problem you are interested in <span className="font-normal text-slate-400">(optional)</span><select value={form.selectedProblem} onChange={(event) => update("selectedProblem", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm"><option value="">I am still deciding</option>{problems.map((problem) => <option key={problem.id} value={problem.id}>{problem.title}</option>)}</select></label>
                  <label className="block text-sm font-semibold text-slate-700">Why do you want to join? <span className="font-normal text-slate-400">(optional)</span><textarea rows={4} maxLength={1000} value={form.motivation} onChange={(event) => update("motivation", event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" placeholder="Your interest, relevant experience, or what you hope to learn." /></label>
                  <label className="flex items-start gap-3 rounded-xl bg-slate-50 p-4 text-sm leading-6 text-slate-600"><input required type="checkbox" checked={form.agreedToRules} onChange={(event) => update("agreedToRules", event.target.checked)} className="mt-1 h-4 w-4 rounded border-slate-300" /><span>I agree to the event rules, code of conduct, and confirm that the information in my profile is accurate.</span></label>
                </div>
                <Button type="submit" disabled={working || !form.agreedToRules} className="mt-6 w-full">{working ? "Registering..." : "Confirm my registration"}</Button>
              </form>
            ) : <aside className="h-fit rounded-3xl border border-slate-200 bg-slate-50 p-6"><h2 className="font-display text-xl font-bold text-slate-900">Registration flow</h2><ol className="mt-5 space-y-4 text-sm text-slate-600">{["Create or complete your participant profile", "Register yourself for this event", "Create, join, or form a solo team", "Team lead locks the roster", "Build and submit the prototype, video, and deck"].map((step, index) => <li key={step} className="flex gap-3"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">{index + 1}</span><span className="pt-1">{step}</span></li>)}</ol></aside>}
          </div>
        </Container>
      </section>
    </>
  );
}
