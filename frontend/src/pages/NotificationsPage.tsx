import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";
import { useNotifications } from "@/hooks/useNotifications";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-PK", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export default function NotificationsPage() {
  const { notifications, loading, error, markRead, markAllRead } = useNotifications();
  const unreadCount = notifications.filter((notification) => !notification.is_read).length;

  return (
    <section className="py-16 sm:py-20">
      <Container size="md">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div><div className="pill bg-brand-50 text-brand-700 ring-1 ring-inset ring-brand-200">Your inbox</div><h1 className="mt-4 font-display text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">Notifications</h1><p className="mt-3 text-slate-600">Important updates about teams, submissions, and hackathons.</p></div>
          {unreadCount > 0 ? <Button type="button" variant="secondary" size="sm" onClick={() => void markAllRead()}>Mark all read</Button> : null}
        </div>
        {error ? <div role="alert" className="mt-8 rounded-xl bg-red-50 p-4 text-sm text-red-700">Notifications are temporarily unavailable.</div> : null}
        <div className="mt-10 space-y-3">
          {loading ? <div className="rounded-2xl border border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">Loading notifications...</div> : null}
          {!loading && notifications.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-10 text-center text-sm text-slate-600">You are all caught up.</div> : null}
          {!loading && notifications.map((notification) => <article key={notification.id} className={`rounded-2xl border p-5 transition ${notification.is_read ? "border-slate-200 bg-white" : "border-brand-200 bg-brand-50/40"}`}><div className="flex items-start justify-between gap-4"><div><div className="flex items-center gap-2"><span className="pill bg-slate-100 text-slate-600">{notification.category}</span>{!notification.is_read ? <span className="h-2 w-2 rounded-full bg-brand-600" aria-label="Unread" /> : null}</div><h2 className="mt-3 font-display text-xl font-semibold text-slate-900">{notification.title}</h2><p className="mt-2 text-sm leading-6 text-slate-600">{notification.body}</p><p className="mt-4 text-xs text-slate-400">{formatDate(notification.created_at)}</p></div>{!notification.is_read ? <Button type="button" variant="ghost" size="sm" onClick={() => void markRead(notification.id)}>Mark read</Button> : null}</div></article>)}
        </div>
      </Container>
    </section>
  );
}
