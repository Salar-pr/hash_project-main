"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, PageHead } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { faDateTime } from "@/lib/date";
import type { CalendarEvent } from "@/lib/types";

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { apiFetch<CalendarEvent[]>("/calendar/").then(setEvents).finally(() => setLoading(false)); }, []);
  return (
    <AppShell>
      <div className="page">
        <PageHead title="تقویم من" desc="رویدادهای عمومی و رویدادهایی که ادمین برای شما ثبت کرده است." />
        <section className="card">
          {loading ? <Loading /> : events.length ? <div className="calendar-list">{events.map((e) => <div className="event-item" key={e.id}><div className="event-date">📅</div><div><b>{e.title}</b><p className="page-desc">{e.description || e.location || "بدون توضیح"}</p></div><div><span className="badge primary">{faDateTime(e.start_at)}</span></div></div>)}</div> : <Empty />}
        </section>
      </div>
    </AppShell>
  );
}
