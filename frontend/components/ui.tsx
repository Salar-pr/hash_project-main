import Link from "next/link";
import type { ReactNode } from "react";

export function StatCard({ label, value, hint, icon = "✦", tone = "primary" }: { label: string; value: ReactNode; hint?: string; icon?: string; tone?: "primary" | "success" | "warning" | "danger" | "info" }) {
  return (
    <div className="card stat">
      <div>
        <div className="stat-label">{label}</div>
        <div className="stat-value">{value}</div>
        {hint ? <div className="stat-hint">{hint}</div> : null}
      </div>
      <div className={`stat-icon ${tone}`}>{icon}</div>
    </div>
  );
}

export function Badge({ children, tone = "primary" }: { children: ReactNode; tone?: "primary" | "success" | "warning" | "danger" | "info" | "neutral" }) {
  return <span className={`badge ${tone === "neutral" ? "" : tone}`}>{children}</span>;
}

export function Loading() {
  return <div className="loading"><div className="spinner" /></div>;
}

export function Empty({ text = "داده‌ای برای نمایش وجود ندارد." }: { text?: string }) {
  return <div className="empty">{text}</div>;
}

export function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: ReactNode }) {
  return (
    <div className="modal-backdrop" onMouseDown={onClose}>
      <div className="modal-card" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>{title}</h3>
          <button className="icon-btn" onClick={onClose} aria-label="close">✕</button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function WeekChart({ data }: { data: Array<{ date: string; hours: number; records?: number }> }) {
  const max = Math.max(1, ...data.map((d) => d.hours));
  return (
    <div className="chart">
      {data.map((d) => (
        <div className="bar-item" key={d.date}>
          <div className="bar-value">{d.hours}h</div>
          <div className="bar" style={{ height: `${Math.max(8, (d.hours / max) * 190)}px` }} />
          <div className="bar-label">{new Date(d.date).toLocaleDateString("fa-IR", { weekday: "short" })}</div>
        </div>
      ))}
    </div>
  );
}

export function PageHead({ title, desc, action }: { title: string; desc?: string; action?: ReactNode }) {
  return (
    <div className="page-head">
      <div>
        <h2 className="page-title">{title}</h2>
        {desc ? <p className="page-desc">{desc}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function Brand({ dark = false }: { dark?: boolean }) {
  return (
    <Link href="/dashboard" className="brand">
      <div className="logo">HR</div>
      <div className="brand-text">
        <strong style={{ color: dark ? "white" : undefined }}>HR Portal</strong>
        <span>Premium Workforce Suite</span>
      </div>
    </Link>
  );
}
