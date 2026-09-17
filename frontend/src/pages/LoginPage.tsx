import { FormEvent, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ApiError, api } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const redirect = new URLSearchParams(location.search).get("redirect");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const tokens = await api.post<{ access: string; refresh: string }>("/accounts/login/", {
        email,
        password,
      }, { redirectOn401: false });
      setTokens(tokens);
      navigate(redirect ? decodeURIComponent(redirect) : "/dashboard", { replace: true });
    } catch (err) {
      const apiError = err as ApiError;
      setError(typeof apiError.data === "string" ? apiError.data : "Unable to sign in with those credentials.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="py-20">
      <Container size="sm">
        <div className="mx-auto max-w-md">
        <h1 className="font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Sign in
        </h1>
        <p className="mt-4 text-base text-slate-600">Return to your build space and keep shipping.</p>
        <form onSubmit={handleSubmit} className="mt-8 space-y-5 rounded-2xl border border-slate-200 bg-white p-6 text-left shadow-soft">
          {error && <div role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
          <label className="block text-sm font-medium text-slate-700">
            Email
            <input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-brand-500" />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Password
            <input required type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 outline-none focus:border-brand-500" />
          </label>
          <Button type="submit" disabled={submitting} className="w-full">{submitting ? "Signing in..." : "Sign in"}</Button>
          <Link to="/password-reset" className="block text-center text-sm font-semibold text-brand-600 hover:underline">
            Forgot your password?
          </Link>
        </form>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <Button to="/" variant="secondary">← Back to Home</Button>
          <Link to="/register" className="text-sm font-semibold text-brand-600 hover:underline">
            Don't have an account? →
          </Link>
        </div>
        </div>
      </Container>
    </section>
  );
}
