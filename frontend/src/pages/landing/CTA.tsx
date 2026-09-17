import { motion } from "framer-motion";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";

export default function CTA() {
  return (
    <section className="py-20 sm:py-24">
      <Container size="md">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br from-brand-700 via-brand-600 to-accent-600 p-8 text-white shadow-glow sm:p-12"
        >
          <div
            className="pointer-events-none absolute inset-0 opacity-20"
            style={{
              backgroundImage:
                "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.6) 1px, transparent 0)",
              backgroundSize: "24px 24px",
            }}
            aria-hidden
          />
          <div className="relative mx-auto max-w-2xl text-center">
            <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
              Find the right KPITB hackathon.
            </h2>
            <p className="mt-4 text-white/85 sm:text-lg">
              Compare active events, read the official challenges, and register yourself before forming a team.
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
              <Button
                to="/hackathons"
                size="lg"
                className="!bg-white !text-brand-700 hover:!bg-brand-50"
                rightIcon={
                  <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M5 12h14M13 5l7 7-7 7" />
                  </svg>
                }
              >
                Browse open events
              </Button>
              <Button
                to="/gallery"
                size="lg"
                className="!bg-white/10 !text-white ring-1 ring-inset ring-white/30 hover:!bg-white/20"
              >
                View Previous Projects
              </Button>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}
