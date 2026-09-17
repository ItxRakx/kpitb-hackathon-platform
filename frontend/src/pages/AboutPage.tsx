import Section from "@/components/ui/Section";

export default function AboutPage() {
  return (
    <Section
      eyebrow="About KPITB Hackathon"
      title="Fostering innovation across Khyber Pakhtunkhwa"
      description="The KPITB Hackathon is the flagship engineering event of the Khyber Pakhtunkhwa Information Technology Board. We bring together students, developers, designers, and domain experts to solve real civic and economic challenges."
    >
      <div className="grid gap-8 md:grid-cols-3">
        {[
          {
            title: "Our Mission",
            body: "Create a thriving tech ecosystem in KP by giving builders a stage, real problems to solve, and capital to keep building.",
          },
          {
            title: "Our Values",
            body: "Fair judging, transparent rules, inclusive community, and zero tolerance for plagiarism. Integrity comes before prizes.",
          },
          {
            title: "Our Partners",
            body: "Universities, industry mentors, and government departments across KP collaborate to make each edition bigger and more impactful.",
          },
        ].map((b) => (
          <div key={b.title} className="card">
            <h3 className="font-display text-lg font-semibold text-slate-900">{b.title}</h3>
            <p className="mt-3 text-sm text-slate-600">{b.body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}
