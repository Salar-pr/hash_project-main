"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Empty, Loading, PageHead } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { faDate } from "@/lib/date";
import type { Task } from "@/lib/types";

const statusFa: Record<string, string> = { todo: "برای انجام", in_progress: "در حال انجام", done: "انجام‌شده", cancelled: "لغو شده" };
const tone = (s: string) => s === "done" ? "success" : s === "in_progress" ? "info" : s === "cancelled" ? "danger" : "warning";

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  async function load() { setLoading(true); setTasks(await apiFetch<Task[]>(`/tasks/${filter ? `?status=${filter}` : ""}`)); setLoading(false); }
  useEffect(() => { load().catch(() => setLoading(false)); }, [filter]);
  async function change(id: number, status: string) { await apiFetch(`/tasks/${id}/status/`, { method: "PATCH", body: JSON.stringify({ status }) }); await load(); }

  return (
    <AppShell>
      <div className="page">
        <PageHead title="تسک‌های من" desc="تسک‌های اختصاص داده‌شده توسط ادمین؛ فقط وضعیت را می‌توانی به‌روزرسانی کنی." action={<select className="select" value={filter} onChange={(e) => setFilter(e.target.value)}><option value="">همه</option><option value="todo">برای انجام</option><option value="in_progress">در حال انجام</option><option value="done">انجام‌شده</option></select>} />
        {loading ? <Loading /> : tasks.length ? <div className="grid three">{tasks.map((t) => <article className="card task-card" key={t.id}><div className="actions" style={{ justifyContent: "space-between" }}><b>{t.title}</b><Badge tone={tone(t.status) as any}>{statusFa[t.status]}</Badge></div><p className="page-desc">{t.description || "بدون توضیح"}</p><div className="task-meta"><Badge tone="neutral">اولویت: {t.priority}</Badge><Badge tone="neutral">مهلت: {faDate(t.due_date)}</Badge></div><select className="select" value={t.status} onChange={(e) => change(t.id, e.target.value)}><option value="todo">برای انجام</option><option value="in_progress">در حال انجام</option><option value="done">انجام‌شده</option><option value="cancelled">لغو شده</option></select></article>)}</div> : <Empty />}
      </div>
    </AppShell>
  );
}
