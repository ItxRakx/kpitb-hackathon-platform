import { motion } from "framer-motion";
import Section from "@/components/ui/Section";

const STEPS = [
  {
    n: "01",
    title: "Choose an event",
    description: "Review its dates, official problems, eligibility, prizes, and team rules before you join.",
  },
  {
    n: "02",
    title: "Register yourself",
    description: "Complete your profile and tell organizers your role, experience, attendance plan, and team preference.",
  },
  {
    n: "03",
    title: "Create or join a team",
    description: "Lead a team, join with an invite, request teammates, or create a solo team. Every member registers first.",
  },
  {
    n: "04",
    title: "Build and submit",
    description: "Deliver a working prototype, short presentation video, and pitch deck before the deadline.",
  },
];

export default function HowItWorks() {
  return (
    <Section
      eyebrow="How It Works"
      title="A registration flow that stays clear"
      description="Account creation, event registration, team formation, and project submission are separate steps."
      className="bg-slate-50/60"
    >
      <ol className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {STEPS.map((s, i) => (
          <motion.li
            key={s.n}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.5, delay: 0.08 * i, ease: "easeOut" }}
            className="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-soft"
          >
            <div className="font-display text-xs font-bold uppercase tracking-[0.2em] text-brand-600">
              Step {s.n}
            </div>
            <h3 className="mt-3 font-display text-lg font-semibold text-slate-900">{s.title}</h3>
            <p className="mt-2 text-sm text-slate-600">{s.description}</p>
          </motion.li>
        ))}
      </ol>
    </Section>
  );
}
