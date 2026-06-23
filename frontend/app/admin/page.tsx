"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Loading, PageHead, StatCard, WeekChart } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import type { DashboardStats, User } from "@/lib/types";

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pending, setPending] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  async function load() {
    setLoading(true);
    const [s, p] = await Promise.all([
      apiFetch<DashboardStats>("/admin-panel/dashboard/stats/"),
      apiFetch<User[]>("/admin-panel/members/?approved=false")
    ]);
    setStats(s); setPending(p); setLoading(false);
  }
  useEffect(() => { load().catch(() => setLoading(false)); }, []);
  async function approve(id: number) { await apiFetch(`/admin-panel/members/${id}/approve/`, { method: "POST" }); await load(); }

  return (
    <AppShell adminOnly>
      <div className="page">
        <PageHead title="پنل ادمین اختصاصی" desc="نمای کلی سازمان، تایید سریع کاربران، چارت هفتگی و دسترسی به عملیات مدیریتی." />
        {loading ? <Loading /> : <>
          <div className="grid cards">
            <StatCard label="کل ممبرها" value={stats?.members_total || 0} icon="👥" />
            <StatCard label="فعال‌ها" value={stats?.members_active || 0} icon="🟢" tone="success" />
            <StatCard label="در انتظار تایید" value={stats?.members_pending_approval || 0} icon="⏳" tone="warning" />
            <StatCard label="تسک‌های باز" value={stats?.tasks_open || 0} icon="✅" tone="info" />
          </div>
          <div className="grid two">
            <section className="card">
              <PageHead title="چارت ساعات هفتگی" desc={`${stats?.weekly_chart.total_hours || 0} ساعت ثبت‌شده`} />
              <WeekChart data={stats?.weekly_chart.by_day || []} />
            </section>
            <section className="card">
              <PageHead title="تایید کاربران جدید" action={<Link className="btn secondary small" href="/admin/members">همه ممبرها</Link>} />
              <div className="table-wrap"><table><thead><tr><th>نام کاربری</th><th>نام</th><th>وضعیت</th><th>عملیات</th></tr></thead><tbody>{pending.slice(0, 6).map((u) => <tr key={u.id}><td>{u.username}</td><td>{u.full_name || "—"}</td><td><Badge tone="warning">منتظر تایید</Badge></td><td><button className="btn success small" onClick={() => approve(u.id)}>تایید</button></td></tr>)}</tbody></table></div>
            </section>
          </div>
          <section className="card">
            <PageHead title="ساعات بر اساس ممبر" />
            <div className="table-wrap"><table><thead><tr><th>کاربر</th><th>نام</th><th>جمع ساعت</th><th>جزئیات</th></tr></thead><tbody>{(stats?.weekly_chart.by_user || []).map((u) => <tr key={u.user_id}><td>{u.username}</td><td>{u.full_name || "—"}</td><td>{u.total_hours}h</td><td><Link className="btn secondary small" href={`/admin/members/${u.user_id}`}>مشاهده</Link></td></tr>)}</tbody></table></div>
          </section>
        </>}
      </div>
    </AppShell>
  );
}
