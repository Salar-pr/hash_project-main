"use client";

import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, Modal, PageHead } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { faDateTime, fromDateTimeLocal, toDateTimeLocal } from "@/lib/date";
import type { CalendarEvent, User } from "@/lib/types";

export default function AdminCalendarPage() {
  const [rows, setRows] = useState<CalendarEvent[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<CalendarEvent | null | "new">(null);
  const [form, setForm] = useState({ title: "", description: "", user: "", start_at: "", end_at: "", location: "" });
  async function load() { setLoading(true); const [r,u] = await Promise.all([apiFetch<CalendarEvent[]>("/admin-panel/calendar-events/"), apiFetch<User[]>("/admin-panel/members/")]); setRows(r); setUsers(u); setLoading(false); }
  useEffect(() => { load().catch(() => setLoading(false)); }, []);
  function openNew() { setEditing("new"); setForm({ title: "", description: "", user: "", start_at: "", end_at: "", location: "" }); }
  function openEdit(e: CalendarEvent) { const u = users.find((x) => x.username === e.username); setEditing(e); setForm({ title: e.title, description: e.description || "", user: String(u?.id || e.user || ""), start_at: toDateTimeLocal(e.start_at), end_at: toDateTimeLocal(e.end_at), location: e.location || "" }); }
  async function save(ev: FormEvent) { ev.preventDefault(); const payload = { ...form, user: form.user ? Number(form.user) : null, start_at: fromDateTimeLocal(form.start_at), end_at: fromDateTimeLocal(form.end_at) }; if (editing === "new") await apiFetch("/admin-panel/calendar-events/", { method: "POST", body: JSON.stringify(payload) }); else if (editing) await apiFetch(`/admin-panel/calendar-events/${editing.id}/`, { method: "PATCH", body: JSON.stringify(payload) }); setEditing(null); await load(); }
  async function remove(e: CalendarEvent) { if (confirm("حذف رویداد؟")) { await apiFetch(`/admin-panel/calendar-events/${e.id}/`, { method: "DELETE" }); await load(); } }
  return <AppShell adminOnly><div className="page"><PageHead title="تقویم سازمانی" desc="ثبت رویداد عمومی یا اختصاصی برای ممبرها." action={<button className="btn" onClick={openNew}>＋ رویداد جدید</button>} />
    <section className="card">{loading ? <Loading /> : rows.length ? <div className="calendar-list">{rows.map((e)=><div className="event-item" key={e.id}><div className="event-date">📅</div><div><b>{e.title}</b><p className="page-desc">{e.description || e.location || "—"}</p></div><div className="actions"><span className="badge primary">{e.username || "عمومی"}</span><span className="badge">{faDateTime(e.start_at)}</span><button className="btn ghost small" onClick={()=>openEdit(e)}>ویرایش</button><button className="btn danger small" onClick={()=>remove(e)}>حذف</button></div></div>)}</div> : <Empty />}</section>
    {editing ? <Modal title={editing === "new" ? "رویداد جدید" : "ویرایش رویداد"} onClose={()=>setEditing(null)}><form className="form-grid" onSubmit={save}><div className="field"><label>عنوان</label><input className="input" value={form.title} onChange={(e)=>setForm({...form,title:e.target.value})} /></div><div className="field"><label>توضیحات</label><textarea className="textarea" value={form.description} onChange={(e)=>setForm({...form,description:e.target.value})} /></div><div className="field"><label>ممبر</label><select className="select" value={form.user} onChange={(e)=>setForm({...form,user:e.target.value})}><option value="">عمومی برای همه</option>{users.map((u)=><option key={u.id} value={u.id}>{u.full_name || u.username}</option>)}</select></div><div className="form-grid two"><div className="field"><label>شروع</label><input className="input" type="datetime-local" value={form.start_at} onChange={(e)=>setForm({...form,start_at:e.target.value})} /></div><div className="field"><label>پایان</label><input className="input" type="datetime-local" value={form.end_at} onChange={(e)=>setForm({...form,end_at:e.target.value})} /></div></div><div className="field"><label>مکان</label><input className="input" value={form.location} onChange={(e)=>setForm({...form,location:e.target.value})} /></div><div className="actions"><button className="btn">ذخیره</button><button type="button" className="btn ghost" onClick={()=>setEditing(null)}>انصراف</button></div></form></Modal> : null}
  </div></AppShell>;
}
