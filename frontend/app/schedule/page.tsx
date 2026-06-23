"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, PageHead } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { addDays, faDate, mondayOf } from "@/lib/date";
import type { Schedule } from "@/lib/types";

export default function SchedulePage() {
  const [week, setWeek] = useState(mondayOf());
  const [rows, setRows] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiFetch<{ records: Schedule[] }>(`/schedules/my/?week_start=${week}`).then((d) => setRows(d.records)).finally(() => setLoading(false));
  }, [week]);

  return (
    <AppShell>
      <div className="page">
        <PageHead title="برنامه هفتگی من" desc="شیفت‌ها توسط ادمین تعیین می‌شوند و اینجا قابل مشاهده‌اند." />
        <section className="card">
          <div className="toolbar" style={{ marginBottom: 16 }}>
            <button className="btn secondary" onClick={() => setWeek(addDays(week, -7))}>هفته قبل</button>
            <input className="input" type="date" value={week} onChange={(e) => setWeek(e.target.value)} />
            <button className="btn secondary" onClick={() => setWeek(addDays(week, 7))}>هفته بعد</button>
            <span className="badge primary">شروع هفته: {faDate(week)}</span>
          </div>
          {loading ? <Loading /> : rows.length ? <div className="table-wrap"><table><thead><tr><th>روز</th><th>شروع شیفت</th><th>پایان شیفت</th></tr></thead><tbody>{rows.map((r) => <tr key={r.id}><td>{r.day_of_week}</td><td>{r.shift_start.slice(0,5)}</td><td>{r.shift_end.slice(0,5)}</td></tr>)}</tbody></table></div> : <Empty text="برنامه‌ای برای این هفته ثبت نشده است." />}
        </section>
      </div>
    </AppShell>
  );
}
