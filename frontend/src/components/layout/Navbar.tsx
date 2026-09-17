import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { isAuthenticated } from "@/lib/auth";

const NAV_LINKS = [
  { to: "/", label: "Home", end: true },
  { to: "/hackathons", label: "Hackathons" },
  { to: "/problems", label: "Problems" },
  { to: "/gallery", label: "Gallery" },
  { to: "/about", label: "About" },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const authed = isAuthenticated();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/60 bg-white/80 backdrop-blur">
      <div className="container-x flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-soft transition group-hover:scale-105">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M13 2 3 14h7l-1 8 10-12h-7z" />
            </svg>
          </div>
          <div className="leading-tight">
            <div className="font-display text-base font-bold tracking-tight text-slate-900">
              KPITB
            </div>
            <div className="text-[10px] font-semibold uppercase tracking-[0.14em] text-brand-600">
              Hackathon
            </div>
          </div>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) =>
                `rounded-lg px-3.5 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          {authed ? <Link to="/dashboard" className="btn-primary">My dashboard</Link> : <><Link to="/login" className="btn-ghost">Sign in</Link><Link to="/hackathons" className="btn-primary">Join a hackathon</Link></>}
        </div>

        <button
          type="button"
          aria-label="Toggle menu"
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-slate-600 hover:bg-slate-100 md:hidden"
          onClick={() => setOpen((v) => !v)}
        >
          <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            {open ? (
              <path d="M6 6l12 12M18 6 6 18" />
            ) : (
              <path d="M4 7h16M4 12h16M4 17h16" />
            )}
          </svg>
        </button>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-slate-200 md:hidden"
          >
            <div className="container-x flex flex-col gap-1 py-3">
              {NAV_LINKS.map((l) => (
                <NavLink
                  key={l.to}
                  to={l.to}
                  end={l.end}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-lg px-3 py-2 text-sm font-medium ${
                      isActive ? "bg-brand-50 text-brand-700" : "text-slate-600 hover:bg-slate-100"
                    }`
                  }
                >
                  {l.label}
                </NavLink>
              ))}
              <div className="mt-2 flex flex-col gap-2 sm:flex-row">
                {authed ? <Link to="/dashboard" onClick={() => setOpen(false)} className="btn-primary">My dashboard</Link> : <><Link to="/login" onClick={() => setOpen(false)} className="btn-secondary">Sign in</Link><Link to="/hackathons" onClick={() => setOpen(false)} className="btn-primary">Join a hackathon</Link></>}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
