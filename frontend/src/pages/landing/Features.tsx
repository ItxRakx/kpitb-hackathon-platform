import { motion } from "framer-motion";
import Section from "@/components/ui/Section";

type Feature = {
  title: string;
  description: string;
  icon: React.ReactNode;
  accent: string;
};

const FEATURES: Feature[] = [
  {
    title: "Official KP Challenges",
    description:
      "Understand the problem, expected deliverables, and difficulty before committing your team to a direction.",
    accent: "from-brand-500 to-brand-400",
    icon: (
      <path d="M17 20h5v-2a4 4 0 0 0-3-3.87M9 20H2v-2a4 4 0 0 1 3-3.87m6-5.13a4 4 0 1 1-8 0 4 4 0 0 1 8 0zm8 0a3 3 0 1 1-6 0 3 3 0 0 1 6 0z" />
    ),
  },
  {
    title: "Individual Event Registration",
    description:
      "Every participant registers with their role, experience, district, attendance plan, and team preference.",
    accent: "from-accent-500 to-fuchsia-400",
    icon: (
      <>
        <rect x="3" y="4" width="18" height="18" rx="2" />
        <path d="M16 2v4M8 2v4M3 10h18" />
      </>
    ),
  },
  {
    title: "Team Formation",
    description:
      "Lead a team, join with an invite code, or build solo. The lead locks the final roster before team registration.",
    accent: "from-sky-500 to-cyan-400",
    icon: (
      <>
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
        <circle cx="12" cy="13" r="3" />
      </>
    ),
  },
  {
    title: "Complete Project Submission",
    description:
      "Submit a working prototype, source link, pitch deck, screenshots, and a recorded or uploaded demo video.",
    accent: "from-emerald-500 to-emerald-400",
    icon: (
      <>
        <path d="M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z" />
      </>
    ),
  },
  {
    title: "Organizer Support",
    description:
      "Ask organizers about registration, a problem statement, your team, or proposal and keep the response in one place.",
    accent: "from-amber-500 to-orange-400",
    icon: (
      <>
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
      </>
    ),
  },
  {
    title: "Transparent Judging",
    description:
      "Projects are reviewed against event-specific criteria, with results published to the public gallery when ready.",
    accent: "from-indigo-500 to-violet-400",
    icon: (
      <>
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <path d="M8 21h8M12 17v4" />
      </>
    ),
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } },
};

export default function Features() {
  return (
    <Section
      eyebrow="Participant journey"
      title="Know what to do at every stage"
      description="The platform keeps event discovery, registration, team formation, submission, and organizer support connected."
    >
      <motion.div
        variants={container}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
        className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        {FEATURES.map((f) => (
          <motion.article key={f.title} variants={item} className="card">
            <div className={`mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${f.accent} text-white shadow-soft`}>
              <svg viewBox="0 0 24 24" fill="none" className="h-6 w-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                {f.icon}
              </svg>
            </div>
            <h3 className="font-display text-lg font-semibold text-slate-900">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">{f.description}</p>
          </motion.article>
        ))}
      </motion.div>
    </Section>
  );
}
