"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Empty, Loading, PageHead, StatCard, WeekChart } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { mondayOf } from "@/lib/date";
import type { Attendance, Schedule, Task } from "@/lib/types";

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [today, setToday] = useState<Attendance | null>(null);
  const [weekly, setWeekly] = useState<{ total_hours: number; records: Attendance[] } | null>(null);
  const [schedule, setSchedule] = useState<{ records: Schedule[] } | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [msg, setMsg] = useState("");

  async function load() {
    setLoading(true);
    const week_start = mondayOf();
    const [todayRes, weeklyRes, scheduleRes, tasksRes] = await Promise.all([
      apiFetch<Attendance | null>("/attendance/today/"),
      apiFetch<{ total_hours: number; records: Attendance[] }>(`/attendance/weekly/?week_start=${week_start}`),
      apiFetch<{ records: Schedule[] }>(`/schedules/my/?week_start=${week_start}`),
      apiFetch<Task[]>("/tasks/")
    ]);
    setToday(todayRes); setWeekly(weeklyRes); setSchedule(scheduleRes); setTasks(tasksRes);
    setLoading(false);
  }

  useEffect(() => { load().catch(() => setLoading(false)); }, []);

  async function punch(type: "in" | "out") {
    setMsg("");
    try {
      const data = await apiFetch<{ detail: string }>(type === "in" ? "/attendance/clock-in/" : "/attendance/clock-out/", { method: "POST" });
      setMsg(data.detail);
      await load();
    } catch (e) { setMsg(e instanceof Error ? e.message : "خطا در ثبت."); }
  }

  return (
    <AppShell>
      <div className="page">
        <PageHead title="داشبورد امروز" desc="ثبت سریع ورود و خروج، مرور ساعت کاری و وضعیت تسک‌ها." action={<div className="actions"><button className="btn success" onClick={() => punch("in")}>⏱ ورود</button><button className="btn danger" onClick={() => punch("out")}>⏹ خروج</button></div>} />
        {msg ? <div className="alert info">{msg}</div> : null}
        {loading ? <Loading /> : (
          <>
            <div className="grid cards">
              <StatCard label="ورود امروز" value={today?.clock_in ? new Date(today.clock_in).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" }) : "—"} icon="⏱" />
              <StatCard label="خروج امروز" value={today?.clock_out ? new Date(today.clock_out).toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" }) : "—"} icon="⏹" tone="success" />
              <StatCard label="ساعت امروز" value={`${today?.hours || 0}h`} icon="⚡" tone="warning" />
              <StatCard label="تسک‌های باز" value={tasks.filter((t) => !["done", "cancelled"].includes(t.status)).length} icon="✅" tone="info" />
            </div>
            <div className="grid two">
              <section className="card">
                <PageHead title="چارت هفتگی" desc={`جمع هفته: ${weekly?.total_hours || 0} ساعت`} />
                <WeekChart data={(weekly?.records || []).map((r) => ({ date: r.work_date, hours: r.hours }))} />
              </section>
              <section className="card">
                <PageHead title="شیفت‌های این هفته" />
                {schedule?.records?.length ? <div className="table-wrap"><table><thead><tr><th>روز</th><th>شروع</th><th>پایان</th></tr></thead><tbody>{schedule.records.slice(0, 5).map((s) => <tr key={s.id}><td>{s.day_of_week}</td><td>{s.shift_start.slice(0,5)}</td><td>{s.shift_end.slice(0,5)}</td></tr>)}</tbody></table></div> : <Empty text="برای این هفته شیفتی ثبت نشده." />}
              </section>
            </div>
            <section className="card">
              <PageHead title="تسک‌های مهم" />
              <div className="grid three">
                {tasks.slice(0, 6).map((t) => <div className="card solid task-card" key={t.id}><b>{t.title}</b><p className="page-desc">{t.description || "بدون توضیح"}</p><div className="task-meta"><Badge tone={t.status === "done" ? "success" : t.status === "in_progress" ? "info" : "warning"}>{t.status}</Badge><Badge tone="neutral">{t.priority}</Badge></div></div>)}
              </div>
            </section>
          </>
        )}
      </div>
    </AppShell>
  );
}
