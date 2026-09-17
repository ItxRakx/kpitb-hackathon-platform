import Hero from "./landing/Hero";
import Features from "./landing/Features";
import HowItWorks from "./landing/HowItWorks";
import CTA from "./landing/CTA";
import { useHackathons } from "@/hooks/useHackathons";
import Section from "@/components/ui/Section";
import Button from "@/components/ui/Button";

export default function LandingPage() {
  const { hackathons, loading } = useHackathons("upcoming");

  return (
    <>
      <Hero />
      <Section eyebrow="The next build window" title="Choose your challenge" description="Hackathons, dates, team sizes, and tracks come directly from the event platform.">
        {loading ? <div className="card text-sm text-slate-500">Loading upcoming hackathons...</div> : hackathons.length === 0 ? <div className="card text-sm text-slate-500">New hackathons will appear here when published.</div> : <div className="grid gap-5 md:grid-cols-2">{hackathons.slice(0, 2).map((hackathon) => <article key={hackathon.id} className="card"><div className="pill bg-brand-50 text-brand-700">{hackathon.is_registration_open ? "Registration open" : "Upcoming"}</div><h2 className="mt-4 font-display text-2xl font-bold text-slate-900">{hackathon.title}</h2><p className="mt-2 text-sm text-slate-600">{hackathon.tagline || "A new opportunity to build with KPITB."}</p><div className="mt-5 flex flex-wrap gap-2">{hackathon.tracks.slice(0, 4).map((track) => <span key={track} className="pill bg-slate-100 text-slate-600">{track}</span>)}</div></article>)}</div>}
        <div className="mt-6"><Button to="/hackathons" variant="secondary">View all hackathons</Button></div>
      </Section>
      <Features />
      <HowItWorks />
      <CTA />
    </>
  );
}
