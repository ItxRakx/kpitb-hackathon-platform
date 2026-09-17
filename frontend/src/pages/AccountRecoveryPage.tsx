import { FormEvent, useState } from "react";
import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api";

export default function AccountRecoveryPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function requestReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    try { await api.post("/accounts/password-reset/", { email }); setMessage("If the account exists, reset instructions have been sent."); } catch (requestError) { setError(requestError instanceof ApiError ? "The reset request could not be completed." : "Network error."); }
  }

  async function confirmReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    try { await api.post("/accounts/password-reset/confirm/", { user_id: Number(userId), token, new_password: password, new_password_confirmation: confirmation }); setMessage("Password reset successfully. You can sign in now."); } catch { setError("The token or password details are invalid."); }
  }

  return <section className="py-16 sm:py-20"><Container size="sm"><div className="pill bg-brand-50 text-brand-700">Account recovery</div><h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900">Reset access.</h1><p className="mt-3 text-slate-600">Request a reset email, then paste the user id and token from the development email or your configured mail provider.</p>{message ? <div role="status" className="mt-8 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">{message}</div> : null}{error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}<form className="card mt-8 space-y-4" onSubmit={requestReset}><h2 className="font-display text-2xl font-semibold text-slate-900">Request reset</h2><label className="block text-sm font-semibold text-slate-700" htmlFor="reset-email">Email</label><input id="reset-email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /><Button type="submit">Send reset instructions</Button></form><form className="card mt-6 space-y-4" onSubmit={confirmReset}><h2 className="font-display text-2xl font-semibold text-slate-900">Set a new password</h2><div className="grid gap-4 sm:grid-cols-2"><div><label className="block text-sm font-semibold text-slate-700" htmlFor="reset-user-id">User id</label><input id="reset-user-id" required value={userId} onChange={(event) => setUserId(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /></div><div><label className="block text-sm font-semibold text-slate-700" htmlFor="reset-token">Token</label><input id="reset-token" required value={token} onChange={(event) => setToken(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /></div></div><label className="block text-sm font-semibold text-slate-700" htmlFor="new-password">New password</label><input id="new-password" type="password" required minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /><label className="block text-sm font-semibold text-slate-700" htmlFor="new-password-confirmation">Confirm password</label><input id="new-password-confirmation" type="password" required minLength={8} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm" /><Button type="submit" variant="secondary">Reset password</Button></form></Container></section>;
}
