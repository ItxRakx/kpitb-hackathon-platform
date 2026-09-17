import { useMemo, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useProblems } from "@/hooks/useProblems";

const difficultyStyle = {
  starter: "bg-emerald-50 text-emerald-700",
  intermediate: "bg-amber-50 text-amber-700",
  advanced: "bg-rose-50 text-rose-700",
};

export default function ProblemStatementsPage() {
  const { problems, loading, error } = useProblems();
  const [category, setCategory] = useState("all");
  const categories = useMemo(() => [...new Set(problems.map((problem) => problem.category))], [problems]);
  const visibleProblems = category === "all" ? problems : problems.filter((problem) => problem.category === category);

  return (
    <section className="py-16 sm:py-20">
      <Container>
        <div className="grid gap-8 border-b border-slate-200 pb-10 lg:grid-cols-[1fr_auto] lg:items-end">
          <div className="max-w-3xl">
            <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Official challenges</div>
            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Problems worth solving for KP.</h1>
            <p className="mt-4 text-base leading-7 text-slate-600">KPITB organizers publish each problem, expected deliverables, and difficulty. Teams choose one before locking their roster.</p>
          </div>
          <Button to="/team">Choose with your team</Button>
        </div>

        <div className="mt-8 flex flex-wrap gap-2" aria-label="Filter problems by category">
          <button type="button" onClick={() => setCategory("all")} className={`rounded-full px-4 py-2 text-sm font-semibold ${category === "all" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>All challenges</button>
          {categories.map((item) => <button key={item} type="button" onClick={() => setCategory(item)} className={`rounded-full px-4 py-2 text-sm font-semibold ${category === item ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>{item}</button>)}
        </div>

        {loading ? <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">Loading official challenges...</div> : null}
        {error ? <div role="alert" className="mt-8 rounded-2xl bg-red-50 p-6 text-sm text-red-700">Problem statements are temporarily unavailable.</div> : null}
        {!loading && !error && visibleProblems.length === 0 ? <div className="mt-8 rounded-2xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-600">No published problem statements match this category yet.</div> : null}

        <div className="mt-8 grid gap-5 lg:grid-cols-2">
          {visibleProblems.map((problem) => (
            <article key={problem.id} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft sm:p-8">
              <div className="flex flex-wrap items-center gap-2">
                <span className="pill bg-brand-50 text-brand-700">{problem.category}</span>
                <span className={`pill capitalize ${difficultyStyle[problem.difficulty]}`}>{problem.difficulty}</span>
                <span className="text-xs font-medium text-slate-400">{problem.hackathon_title}</span>
              </div>
              <h2 className="mt-5 font-display text-2xl font-bold text-slate-900">{problem.title}</h2>
              <p className="mt-3 text-sm leading-6 text-slate-600">{problem.summary}</p>
              {problem.description ? <details className="mt-6 rounded-2xl bg-slate-50 p-4"><summary className="cursor-pointer text-sm font-semibold text-slate-900">Read full problem brief</summary><p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">{problem.description}</p>{problem.deliverables ? <div className="mt-4 border-t border-slate-200 pt-4"><p className="text-xs font-bold uppercase tracking-wider text-slate-500">Expected deliverables</p><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">{problem.deliverables}</p></div> : null}</details> : null}
            </article>
          ))}
        </div>
      </Container>
    </section>
  );
}
