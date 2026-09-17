import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { ApiError, api } from "@/lib/api";

function messageFromError(error: unknown) {
  if (error instanceof ApiError && error.data && typeof error.data === "object") {
    const values = Object.values(error.data as Record<string, unknown>).flat();
    const first = values.find((value) => typeof value === "string");
    if (typeof first === "string") return first;
  }
  return "We could not create your account. Please check the form and try again.";
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const redirect = new URLSearchParams(location.search).get("redirect");
  const [form, setForm] = useState({
    fullName: "", email: "", phone: "", district: "", institution: "",
    educationLevel: "", skills: "", password: "", confirmPassword: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    const [firstName, ...lastNameParts] = form.fullName.trim().split(/\s+/);
    if (!lastNameParts.length) {
      setError("Please enter your first and last name.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await api.post("/accounts/register/", {
        email: form.email,
        password1: form.password,
        password2: form.confirmPassword,
        first_name: firstName,
        last_name: lastNameParts.join(" "),
        phone: form.phone,
        district: form.district,
        institution: form.institution,
        education_level: form.educationLevel,
        skills: form.skills.split(",").map((skill) => skill.trim()).filter(Boolean),
      }, { redirectOn401: false });
      navigate(`/login${redirect ? `?redirect=${redirect}` : ""}`, { replace: true, state: { registered: true } });
    } catch (requestError) {
      setError(messageFromError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  const fieldClass = "mt-1.5 w-full rounded-xl border border-slate-300 px-3.5 py-3 text-base outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100";

  return (
    <section className="py-14 sm:py-20">
      <Container size="md">
        <div className="grid gap-10 lg:grid-cols-[0.75fr_1.25fr] lg:items-start">
          <div className="lg:sticky lg:top-24">
            <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Participant registration</div>
            <h1 className="mt-5 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Start with a useful profile.</h1>
            <p className="mt-4 text-base leading-7 text-slate-600">Your district, institution, and skills help team leads across Khyber Pakhtunkhwa find the right people.</p>
            <ol className="mt-8 space-y-4 text-sm text-slate-600">
              {[
                "Create and verify your participant account",
                "Choose an organizer-published problem",
                "Lead a team or join with an invite",
                "Lock the roster and submit your proposal",
              ].map((step, index) => (
                <li key={step} className="flex gap-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white">{index + 1}</span>
                  <span className="pt-1">{step}</span>
                </li>
              ))}
            </ol>
          </div>

          <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-white p-6 text-left shadow-soft sm:p-8">
            {error ? <div role="alert" className="mb-6 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div> : null}
            <div className="grid gap-5 sm:grid-cols-2">
              <label className="block text-sm font-semibold text-slate-700 sm:col-span-2">Full name
                <input required minLength={3} value={form.fullName} onChange={(event) => update("fullName", event.target.value)} className={fieldClass} autoComplete="name" placeholder="First and last name" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Email
                <input required type="email" value={form.email} onChange={(event) => update("email", event.target.value)} className={fieldClass} autoComplete="email" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Phone
                <input required value={form.phone} onChange={(event) => update("phone", event.target.value)} className={fieldClass} autoComplete="tel" placeholder="03XX XXXXXXX" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">District
                <input required value={form.district} onChange={(event) => update("district", event.target.value)} className={fieldClass} placeholder="e.g. Peshawar, Swat" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Institution / organization
                <input required value={form.institution} onChange={(event) => update("institution", event.target.value)} className={fieldClass} placeholder="University, college, or company" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Education level
                <select required value={form.educationLevel} onChange={(event) => update("educationLevel", event.target.value)} className={`${fieldClass} bg-white`}>
                  <option value="">Choose one</option>
                  <option value="school">School</option>
                  <option value="college">College</option>
                  <option value="undergraduate">Undergraduate</option>
                  <option value="graduate">Graduate</option>
                  <option value="professional">Professional</option>
                </select>
              </label>
              <label className="block text-sm font-semibold text-slate-700">Skills
                <input required value={form.skills} onChange={(event) => update("skills", event.target.value)} className={fieldClass} placeholder="React, UI design, Python" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Password
                <input required minLength={8} type="password" value={form.password} onChange={(event) => update("password", event.target.value)} className={fieldClass} autoComplete="new-password" />
              </label>
              <label className="block text-sm font-semibold text-slate-700">Confirm password
                <input required minLength={8} type="password" value={form.confirmPassword} onChange={(event) => update("confirmPassword", event.target.value)} className={fieldClass} autoComplete="new-password" />
              </label>
            </div>
            <p className="mt-5 text-xs leading-5 text-slate-500">Only organizers and your team can use your contact details. Public project pages do not show your phone number.</p>
            <Button type="submit" disabled={submitting} className="mt-6 w-full">{submitting ? "Creating account..." : "Create participant account"}</Button>
            <p className="mt-5 text-center text-sm text-slate-600">Already registered? <Link to="/login" className="font-semibold text-brand-700 hover:underline">Sign in</Link></p>
          </form>
        </div>
      </Container>
    </section>
  );
}
