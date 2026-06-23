"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Empty, Loading, PageHead, StatCard, WeekChart } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { faDate, faDateTime, mondayOf, timeOnly } from "@/lib/date";
import type { Attendance, CalendarEvent, Schedule, Task, User } from "@/lib/types";

type FullInfo = { user: User; week_start: string; week_end: string; attendance_total_hours: number; attendance: Attendance[]; schedule: Schedule[]; tasks: Task[]; calendar_events: CalendarEvent[] };

export default function MemberDetailPage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<FullInfo | null>(null);
  const [week, setWeek] = useState(mondayOf());
  const [loading, setLoading] = useState(true);
  useEffect(() => { setLoading(true); apiFetch<FullInfo>(`/admin-panel/members/${params.id}/full-info/?week_start=${week}`).then(setData).finally(() => setLoading(false)); }, [params.id, week]);
  return (
    <AppShell adminOnly>
      <div className="page">
        <PageHead title={`جزئیات ممبر ${data?.user.username || ""}`} desc="اطلاعات کامل کاربر، حقوق روبل، ورود/خروج، شیفت‌ها، تسک‌ها و تقویم." action={<Link className="btn secondary" href="/admin/members">بازگشت</Link>} />
        {loading ? <Loading /> : data ? <>
          <div className="grid cards">
            <StatCard label="نام" value={data.user.full_name || data.user.username} icon="👤" />
            <StatCard label="حقوق روبل" value={data.user.salary_ruble ? `${data.user.salary_ruble} ₽` : "—"} icon="₽" tone="success" />
            <StatCard label="ساعت هفته" value={`${data.attendance_total_hours}h`} icon="⚡" tone="warning" />
            <StatCard label="تسک‌ها" value={data.tasks.length} icon="✅" tone="info" />
          </div>
          <section className="card"><PageHead title="پروفایل" /><div className="grid three"><div><b>نقش</b><p><Badge tone={data.user.role === "admin" ? "primary" : "neutral"}>{data.user.role}</Badge></p></div><div><b>تایید</b><p><Badge tone={data.user.is_approved ? "success" : "warning"}>{data.user.is_approved ? "تایید شده" : "منتظر"}</Badge></p></div><div><b>ایجاد</b><p>{faDateTime(data.user.created_at)}</p></div><div><b>ایمیل</b><p>{data.user.email || "—"}</p></div><div><b>تلفن</b><p>{data.user.phone || "—"}</p></div><div><b>دپارتمان</b><p>{data.user.department || "—"}</p></div></div></section>
          <div className="grid two">
            <section className="card"><PageHead title="چارت این هفته" action={<input className="input" type="date" value={week} onChange={(e) => setWeek(e.target.value)} />} /><WeekChart data={data.attendance.map((r) => ({ date: r.work_date, hours: r.hours }))} /></section>
            <section className="card"><PageHead title="برنامه هفته" />{data.schedule.length ? <div className="table-wrap"><table><thead><tr><th>روز</th><th>شروع</th><th>پایان</th></tr></thead><tbody>{data.schedule.map((s) => <tr key={s.id}><td>{s.day_of_week}</td><td>{s.shift_start.slice(0,5)}</td><td>{s.shift_end.slice(0,5)}</td></tr>)}</tbody></table></div> : <Empty />}</section>
          </div>
          <section className="card"><PageHead title="ورود و خروج" />{data.attendance.length ? <div className="table-wrap"><table><thead><tr><th>تاریخ</th><th>ورود</th><th>خروج</th><th>ساعت</th></tr></thead><tbody>{data.attendance.map((a) => <tr key={a.id}><td>{faDate(a.work_date)}</td><td>{timeOnly(a.clock_in)}</td><td>{timeOnly(a.clock_out)}</td><td>{a.hours}</td></tr>)}</tbody></table></div> : <Empty />}</section>
          <section className="card"><PageHead title="تسک‌ها" />{data.tasks.length ? <div className="grid three">{data.tasks.map((t) => <div className="card solid" key={t.id}><b>{t.title}</b><p className="page-desc">{t.description || "—"}</p><Badge tone={t.status === "done" ? "success" : "warning"}>{t.status}</Badge></div>)}</div> : <Empty />}</section>
          <section className="card"><PageHead title="تقویم" />{data.calendar_events.length ? <div className="calendar-list">{data.calendar_events.map((e) => <div className="event-item" key={e.id}><div className="event-date">📅</div><div><b>{e.title}</b><p className="page-desc">{e.description || e.location || "—"}</p></div><Badge>{faDateTime(e.start_at)}</Badge></div>)}</div> : <Empty />}</section>
        </> : <Empty />}
      </div>
    </AppShell>
  );
}
