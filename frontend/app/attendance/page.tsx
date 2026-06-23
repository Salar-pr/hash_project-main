"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, PageHead, StatCard } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { addDays, faDate, mondayOf, timeOnly } from "@/lib/date";
import type { Attendance } from "@/lib/types";

export default function AttendancePage() {
  const [week, setWeek] = useState(mondayOf());
  const [data, setData] = useState<{ week_start: string; week_end: string; total_hours: number; records: Attendance[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");

  async function load() {
    setLoading(true);
    setData(await apiFetch(`/attendance/weekly/?week_start=${week}`));
    setLoading(false);
  }
  useEffect(() => { load().catch(() => setLoading(false)); }, [week]);

  async function punch(type: "in" | "out") {
    try {
      const res = await apiFetch<{ detail: string }>(type === "in" ? "/attendance/clock-in/" : "/attendance/clock-out/", { method: "POST" });
      setMsg(res.detail); await load();
    } catch (e) { setMsg(e instanceof Error ? e.message : "خطا"); }
  }

  return (
    <AppShell>
      <div className="page">
        <PageHead title="حضور و غیاب" desc="ثبت ورود و خروج و مرور رکوردهای هفتگی." action={<div className="actions"><button className="btn success" onClick={() => punch("in")}>ثبت ورود</button><button className="btn danger" onClick={() => punch("out")}>ثبت خروج</button></div>} />
        {msg ? <div className="alert info">{msg}</div> : null}
        <div className="grid cards">
          <StatCard label="شروع هفته" value={faDate(week)} icon="📅" />
          <StatCard label="پایان هفته" value={faDate(addDays(week, 6))} icon="🗓" tone="info" />
          <StatCard label="جمع ساعات" value={`${data?.total_hours || 0}h`} icon="⚡" tone="warning" />
          <StatCard label="رکوردها" value={data?.records.length || 0} icon="📌" tone="success" />
        </div>
        <section className="card">
          <div className="toolbar" style={{ marginBottom: 16 }}>
            <button className="btn secondary" onClick={() => setWeek(addDays(week, -7))}>هفته قبل</button>
            <input className="input" type="date" value={week} onChange={(e) => setWeek(e.target.value)} />
            <button className="btn secondary" onClick={() => setWeek(addDays(week, 7))}>هفته بعد</button>
          </div>
          {loading ? <Loading /> : data?.records.length ? <div className="table-wrap"><table><thead><tr><th>تاریخ</th><th>ورود</th><th>خروج</th><th>ساعت</th></tr></thead><tbody>{data.records.map((r) => <tr key={r.id}><td>{faDate(r.work_date)}</td><td>{timeOnly(r.clock_in)}</td><td>{timeOnly(r.clock_out)}</td><td>{r.hours}h</td></tr>)}</tbody></table></div> : <Empty />}
        </section>
      </div>
    </AppShell>
  );
}
