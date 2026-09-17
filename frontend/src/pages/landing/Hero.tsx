import { motion } from "framer-motion";
import Button from "@/components/ui/Button";

const FADE_UP = {
  hidden: { opacity: 0, y: 16 },
  show: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.08 * i, duration: 0.5, ease: "easeOut" },
  }),
};

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-hero-gradient">
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage:
            "radial-gradient(circle at 1px 1px, rgba(30,64,175,0.15) 1px, transparent 0)",
          backgroundSize: "28px 28px",
        }}
        aria-hidden
      />
      <div className="relative container-x py-20 sm:py-28 lg:py-32">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <motion.div
              custom={0}
              variants={FADE_UP}
              initial="hidden"
              animate="show"
            >
              <div className="pill mb-6 bg-white text-brand-700 ring-1 ring-inset ring-brand-200 shadow-soft">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-brand-500" />
                </span>
                KPITB Hackathons - Registration open
              </div>
            </motion.div>

            <motion.h1
              custom={1}
              variants={FADE_UP}
              initial="hidden"
              animate="show"
              className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl"
            >
              Build something useful for{" "}
              <span className="bg-gradient-to-r from-brand-600 via-brand-500 to-accent-500 bg-clip-text text-transparent">
                Khyber Pakhtunkhwa.
              </span>
            </motion.h1>

            <motion.p
              custom={2}
              variants={FADE_UP}
              initial="hidden"
              animate="show"
              className="mt-6 max-w-xl text-base text-slate-600 sm:text-lg"
            >
              Choose an official problem, register your participant profile, form a team of up to six,
              and turn your idea into a working prototype with support from KPITB.
            </motion.p>

            <motion.div
              custom={3}
              variants={FADE_UP}
              initial="hidden"
              animate="show"
              className="mt-8 flex flex-wrap items-center gap-3"
            >
              <Button
                to="/hackathons"
                size="lg"
                rightIcon={
                  <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 5l7 7-7 7" />
                  </svg>
                }
              >
                Explore hackathons
              </Button>
              <Button to="/problems" variant="secondary" size="lg">
                View problems
              </Button>
            </motion.div>

            <motion.dl
              custom={4}
              variants={FADE_UP}
              initial="hidden"
              animate="show"
              className="mt-12 grid grid-cols-3 gap-6 max-w-lg"
            >
              {[
                { value: "KP-wide", label: "Participation" },
                { value: "1-6", label: "Team Size" },
                { value: "3", label: "Final Deliverables" },
              ].map((s) => (
                <div key={s.label}>
                  <dt className="text-xs font-medium uppercase tracking-wider text-slate-500">{s.label}</dt>
                  <dd className="mt-1 font-display text-2xl font-bold text-slate-900">{s.value}</dd>
                </div>
              ))}
            </motion.dl>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
            className="relative"
          >
            <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-brand-200/60 via-white to-accent-200/60 blur-2xl" />
            <div className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white/80 shadow-glow backdrop-blur">
              <div className="flex items-center gap-1.5 border-b border-slate-200 bg-slate-50/70 px-4 py-3">
                <div className="flex gap-1.5">
                  <span className="h-3 w-3 rounded-full bg-red-400" />
                  <span className="h-3 w-3 rounded-full bg-amber-400" />
                  <span className="h-3 w-3 rounded-full bg-emerald-400" />
                </div>
                <div className="ml-3 truncate rounded-md bg-white px-3 py-1 text-xs text-slate-500 ring-1 ring-inset ring-slate-200">
                  Your registration journey
                </div>
              </div>
              <div className="space-y-4 p-6">
                <div className="rounded-2xl border border-slate-200 p-4">
                  <div className="mb-3 flex items-center justify-between">
                    <div className="text-sm font-semibold text-slate-800">How registration works</div>
                    <span className="pill bg-brand-50 text-brand-700">5 steps</span>
                  </div>
                  <ol className="space-y-3">
                    {[
                      ["01", "Choose a hackathon", "Review dates, rules, prizes, and problems."],
                      ["02", "Complete your profile", "Add district, institution, role, and skills."],
                      ["03", "Register yourself", "Tell us how you want to participate."],
                      ["04", "Create or join a team", "Every member registers individually."],
                      ["05", "Build and submit", "Prototype, short video, and pitch deck."],
                    ].map(([number, title, copy]) => (
                      <li key={number} className="flex items-start gap-3 rounded-xl bg-slate-50 p-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-900 font-mono text-xs font-bold text-white">{number}</div>
                        <div><p className="text-sm font-semibold text-slate-900">{title}</p><p className="mt-1 text-xs leading-5 text-slate-500">{copy}</p></div>
                      </li>
                    ))}
                  </ol>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
