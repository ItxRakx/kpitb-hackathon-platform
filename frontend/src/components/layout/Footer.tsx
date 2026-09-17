import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="container-x py-10 grid gap-8 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-500 text-white shadow-soft">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M13 2 3 14h7l-1 8 10-12h-7z" />
              </svg>
            </div>
            <div>
              <div className="font-display text-base font-bold">KPITB Hackathon</div>
              <div className="text-xs text-slate-500">Khyber Pakhtunkhwa Information Technology Board</div>
            </div>
          </div>
          <p className="mt-4 max-w-md text-sm text-slate-600">
            Empowering innovators across KP to build the next generation of digital solutions.
            Join our hackathons, collaborate with the best, and ship products that matter.
          </p>
        </div>

        <div>
          <div className="text-sm font-semibold text-slate-900">Platform</div>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li><Link to="/" className="hover:text-brand-600">Home</Link></li>
            <li><Link to="/gallery" className="hover:text-brand-600">Project Gallery</Link></li>
            <li><Link to="/about" className="hover:text-brand-600">About</Link></li>
            <li><Link to="/login" className="hover:text-brand-600">Sign in</Link></li>
          </ul>
        </div>

        <div>
          <div className="text-sm font-semibold text-slate-900">Resources</div>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            <li><span className="hover:text-brand-600 cursor-not-allowed">Rules &amp; FAQs</span></li>
            <li><span className="hover:text-brand-600 cursor-not-allowed">Judging Criteria</span></li>
            <li><span className="hover:text-brand-600 cursor-not-allowed">Contact</span></li>
            <li><span className="hover:text-brand-600 cursor-not-allowed">Code of Conduct</span></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-slate-200 py-5">
        <div className="container-x flex flex-col items-start justify-between gap-2 text-xs text-slate-500 sm:flex-row sm:items-center">
          <p>© {new Date().getFullYear()} KPITB. All rights reserved.</p>
          <p>Built with React, Vite, Tailwind CSS, and Django.</p>
        </div>
      </div>
    </footer>
  );
}
