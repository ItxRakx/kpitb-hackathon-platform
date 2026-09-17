import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useUser } from "@/hooks/useAuth";
import { ApiError, api } from "@/lib/api";

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user, loading, refetch } = useUser();
  const [form, setForm] = useState({
    firstName: "", lastName: "", phone: "", district: "", institution: "",
    educationLevel: "", skills: "", bio: "", portfolioUrl: "", githubUrl: "",
  });
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    setForm({
      firstName: user.first_name || "",
      lastName: user.last_name || "",
      phone: user.profile?.phone || "",
      district: user.profile?.district || "",
      institution: user.profile?.institution || "",
      educationLevel: user.profile?.education_level || "",
      skills: user.profile?.skills?.join(", ") || "",
      bio: user.profile?.bio || "",
      portfolioUrl: user.profile?.portfolio_url || "",
      githubUrl: user.profile?.github_url || "",
    });
  }, [user]);

  function update(field: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setWorking(true);
    setError("");
    setMessage("");
    try {
      await api.patch("/accounts/me/", {
        first_name: form.firstName,
        last_name: form.lastName,
        profile: {
          phone: form.phone,
          district: form.district,
          institution: form.institution,
          education_level: form.educationLevel,
          skills: form.skills.split(",").map((skill) => skill.trim()).filter(Boolean),
          bio: form.bio,
          portfolio_url: form.portfolioUrl || null,
          github_url: form.githubUrl || null,
        },
      });
      await refetch();
      setMessage("Your participant profile has been updated.");
    } catch (requestError) {
      setError(requestError instanceof ApiError ? "Please check the profile fields and try again." : "Profile could not be updated.");
    } finally {
      setWorking(false);
    }
  }

  const fieldClass = "mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-base outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100";

  return (
    <section className="py-16 sm:py-20">
      <Container size="md">
        <Button type="button" variant="ghost" size="sm" onClick={() => navigate("/dashboard")} className="!px-0">Back to dashboard</Button>
        <div className="mt-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Participant profile</div>
            <h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Show teams what you bring.</h1>
            <p className="mt-3 max-w-2xl text-slate-600">Keep your skills and background current. Personal contact details stay out of the public gallery.</p>
          </div>
          <span className={`pill ${user?.profile?.is_complete ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>{user?.profile?.is_complete ? "Profile complete" : "Profile needs details"}</span>
        </div>

        {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}
        {message ? <div role="status" className="mt-8 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">{message}</div> : null}
        <form onSubmit={save} className="card mt-8 space-y-6">
          {loading ? <p className="text-sm text-slate-500">Loading your profile...</p> : null}
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="text-sm font-semibold text-slate-700">First name<input required value={form.firstName} onChange={(event) => update("firstName", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">Last name<input required value={form.lastName} onChange={(event) => update("lastName", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">Phone<input required value={form.phone} onChange={(event) => update("phone", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">District<input required value={form.district} onChange={(event) => update("district", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">Institution / organization<input required value={form.institution} onChange={(event) => update("institution", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">Education level<input value={form.educationLevel} onChange={(event) => update("educationLevel", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700 sm:col-span-2">Skills<input required value={form.skills} onChange={(event) => update("skills", event.target.value)} className={fieldClass} placeholder="Comma-separated: Python, UX research, pitching" /></label>
            <label className="text-sm font-semibold text-slate-700 sm:col-span-2">Short bio<textarea rows={4} value={form.bio} onChange={(event) => update("bio", event.target.value)} className={fieldClass} placeholder="What do you enjoy building and how can you help a team?" /></label>
            <label className="text-sm font-semibold text-slate-700">Portfolio URL<input type="url" value={form.portfolioUrl} onChange={(event) => update("portfolioUrl", event.target.value)} className={fieldClass} /></label>
            <label className="text-sm font-semibold text-slate-700">GitHub URL<input type="url" value={form.githubUrl} onChange={(event) => update("githubUrl", event.target.value)} className={fieldClass} /></label>
          </div>
          <div className="flex justify-end border-t border-slate-100 pt-5"><Button type="submit" disabled={working || loading}>{working ? "Saving..." : "Save profile"}</Button></div>
        </form>
      </Container>
    </section>
  );
}
