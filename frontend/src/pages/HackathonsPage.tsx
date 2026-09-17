import { useMemo, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useHackathons } from "@/hooks/useHackathons";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-PK", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

type Filter = "all" | "registering" | "live" | "past";

export default function HackathonsPage() {
  const { hackathons, loading, error } = useHackathons();
  const [filter, setFilter] = useState<Filter>("all");
  const [search, setSearch] = useState("");

  const visible = useMemo(() => {
    const query = search.trim().toLowerCase();
    return hackathons.filter((hackathon) => {
      const matchesQuery = !query || `${hackathon.title} ${hackathon.tagline} ${hackathon.tracks.join(" ")}`.toLowerCase().includes(query);
      const matchesFilter = filter === "all"
        || (filter === "registering" && hackathon.is_registration_open)
        || (filter === "live" && hackathon.is_ongoing)
        || (filter === "past" && hackathon.is_completed);
      return matchesQuery && matchesFilter;
    });
  }, [filter, hackathons, search]);

  return (
    <section className="py-14 sm:py-20">
      <Container>
        <div className="grid gap-8 border-b border-slate-200 pb-10 lg:grid-cols-[1fr_420px] lg:items-end">
          <div className="max-w-3xl">
            <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">KPITB hackathons</div>
            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-950 sm:text-6xl">Choose an event before you register.</h1>
            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-600">Review the dates, eligibility, problems, prizes, and team rules first. Your registration will stay attached to the event you select.</p>
          </div>
          <label className="block text-sm font-semibold text-slate-700">Find a hackathon
            <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} className="mt-2 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-base outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100" placeholder="Search by title, track, or topic" />
          </label>
        </div>

        <div className="mt-7 flex flex-wrap gap-2" aria-label="Filter hackathons">
          {(["all", "registering", "live", "past"] as Filter[]).map((item) => (
            <button key={item} type="button" onClick={() => setFilter(item)} className={`rounded-full px-4 py-2 text-sm font-semibold capitalize transition ${filter === item ? "bg-slate-950 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>{item === "registering" ? "Registration open" : item}</button>
          ))}
        </div>

        {loading ? <div className="mt-8 rounded-3xl border border-slate-200 bg-slate-50 p-12 text-center text-sm text-slate-500">Loading hackathons...</div> : null}
        {error ? <div role="alert" className="mt-8 rounded-3xl bg-red-50 p-8 text-center text-sm text-red-700">Hackathons are temporarily unavailable.</div> : null}
        {!loading && !error && visible.length === 0 ? <div className="mt-8 rounded-3xl border border-dashed border-slate-300 p-12 text-center text-sm text-slate-600">No hackathons match this filter.</div> : null}

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          {visible.map((hackathon) => (
            <article key={hackathon.id} className="group overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-soft transition hover:-translate-y-1 hover:border-brand-200 hover:shadow-glow">
              <div className="bg-slate-950 p-6 text-white sm:p-8">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className={`pill ${hackathon.is_registration_open ? "bg-emerald-400 text-emerald-950" : hackathon.is_ongoing ? "bg-amber-300 text-amber-950" : "bg-white/10 text-white"}`}>{hackathon.is_registration_open ? "Registration open" : hackathon.is_ongoing ? "Live now" : hackathon.is_completed ? "Completed" : "Upcoming"}</span>
                  <span className="text-sm font-medium text-slate-300">{formatDate(hackathon.starts_at)} - {formatDate(hackathon.ends_at)}</span>
                </div>
                <h2 className="mt-6 font-display text-3xl font-bold tracking-tight">{hackathon.title}</h2>
                <p className="mt-3 min-h-12 text-sm leading-6 text-slate-300">{hackathon.tagline || "Build a useful solution for Khyber Pakhtunkhwa."}</p>
              </div>
              <div className="p-6 sm:p-8">
                <dl className="grid grid-cols-3 gap-4 text-sm">
                  <div><dt className="text-slate-500">Participants</dt><dd className="mt-1 font-display text-xl font-bold text-slate-900">{hackathon.participant_count}</dd></div>
                  <div><dt className="text-slate-500">Teams</dt><dd className="mt-1 font-display text-xl font-bold text-slate-900">{hackathon.team_count}</dd></div>
                  <div><dt className="text-slate-500">Problems</dt><dd className="mt-1 font-display text-xl font-bold text-slate-900">{hackathon.problem_count}</dd></div>
                </dl>
                <div className="mt-6 flex flex-wrap gap-2">{hackathon.tracks.slice(0, 4).map((track) => <span key={track} className="pill bg-slate-100 text-slate-600">{track}</span>)}</div>
                <div className="mt-7 flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-6">
                  <p className="text-sm text-slate-500">Teams of <span className="font-semibold text-slate-900">{hackathon.team_min_size}-{hackathon.team_max_size}</span></p>
                  <Button to={`/hackathons/${hackathon.slug}`} size="sm">View event & register</Button>
                </div>
              </div>
            </article>
          ))}
        </div>
      </Container>
    </section>
  );
}
