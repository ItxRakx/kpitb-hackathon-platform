import type { ReactNode } from "react";
import Container from "./Container";

type Props = {
  eyebrow?: string;
  title: string;
  description?: string;
  children?: ReactNode;
  align?: "left" | "center";
  id?: string;
  className?: string;
};

export default function Section({
  eyebrow,
  title,
  description,
  children,
  align = "left",
  id,
  className = "",
}: Props) {
  const centered = align === "center";
  return (
    <section id={id} className={`py-20 sm:py-24 ${className}`}>
      <Container size="lg">
        <div className={`mb-12 ${centered ? "mx-auto max-w-2xl text-center" : "max-w-2xl"}`}>
          {eyebrow && (
            <div className="pill mb-4 bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">
              <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
              {eyebrow}
            </div>
          )}
          <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {title}
          </h2>
          {description && (
            <p className="mt-4 text-base text-slate-600 sm:text-lg">{description}</p>
          )}
        </div>
        {children}
      </Container>
    </section>
  );
}
