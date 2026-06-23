"use client";

import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, Modal, PageHead } from "@/components/ui";
import { apiFetch, query } from "@/lib/api";
import { addDays, mondayOf } from "@/lib/date";
import type { Schedule, User } from "@/lib/types";

const days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

export default function AdminSchedulesPage() {
  const [week, setWeek] = useState(mondayOf());
  const [rows, setRows] = useState<Schedule[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Schedule | null | "new">(null);
  const [form, setForm] = useState({ user: "", week_start: week, day_of_week: "Monday", shift_start: "09:00", shift_end: "18:00" });
  async function load() { setLoading(true); const [r,u] = await Promise.all([apiFetch<Schedule[]>(`/admin-panel/schedules/${query({ week_start: week })}`), apiFetch<User[]>("/admin-panel/members/")]); setRows(r); setUsers(u); setLoading(false); }
  useEffect(() => { load().catch(() => setLoading(false)); }, [week]);
  function openNew() { setEditing("new"); setForm({ user: users[0]?.id ? String(users[0].id) : "", week_start: week, day_of_week: "Monday", shift_start: "09:00", shift_end: "18:00" }); }
  function openEdit(r: Schedule) { const u = users.find((x) => x.username === r.username); setEditing(r); setForm({ user: String(u?.id || r.user), week_start: r.week_start, day_of_week: r.day_of_week, shift_start: r.shift_start.slice(0,5), shift_end: r.shift_end.slice(0,5) }); }
  async function save(e: FormEvent) { e.preventDefault(); const payload = { ...form, user: Number(form.user) }; if (editing === "new") await apiFetch("/admin-panel/schedules/", { method: "POST", body: JSON.stringify(payload) }); else if (editing) await apiFetch(`/admin-panel/schedules/${editing.id}/`, { method: "PATCH", body: JSON.stringify(payload) }); setEditing(null); await load(); }
  async function remove(r: Schedule) { if (confirm("حذف شیفت؟")) { await apiFetch(`/admin-panel/schedules/${r.id}/`, { method: "DELETE" }); await load(); } }
  return <AppShell adminOnly><div className="page"><PageHead title="مدیریت شیفت‌ها" desc="تعریف یا تغییر برنامه هفتگی همه ممبرها." action={<button className="btn" onClick={openNew}>＋ شیفت جدید</button>} />
    <section className="card"><div className="toolbar" style={{ marginBottom: 16 }}><button className="btn secondary" onClick={() => setWeek(addDays(week,-7))}>هفته قبل</button><input className="input" type="date" value={week} onChange={(e)=>setWeek(e.target.value)} /><button className="btn secondary" onClick={() => setWeek(addDays(week,7))}>هفته بعد</button></div>{loading ? <Loading /> : rows.length ? <div className="table-wrap"><table><thead><tr><th>کاربر</th><th>هفته</th><th>روز</th><th>شروع</th><th>پایان</th><th>عملیات</th></tr></thead><tbody>{rows.map((r)=><tr key={r.id}><td>{r.username}</td><td>{r.week_start}</td><td>{r.day_of_week}</td><td>{r.shift_start.slice(0,5)}</td><td>{r.shift_end.slice(0,5)}</td><td><div className="actions"><button className="btn ghost small" onClick={()=>openEdit(r)}>ویرایش</button><button className="btn danger small" onClick={()=>remove(r)}>حذف</button></div></td></tr>)}</tbody></table></div> : <Empty />}</section>
    {editing ? <Modal title={editing === "new" ? "شیفت جدید" : "ویرایش شیفت"} onClose={()=>setEditing(null)}><form className="form-grid" onSubmit={save}><div className="field"><label>ممبر</label><select className="select" value={form.user} onChange={(e)=>setForm({...form,user:e.target.value})}>{users.map((u)=><option key={u.id} value={u.id}>{u.full_name || u.username}</option>)}</select></div><div className="form-grid two"><div className="field"><label>شروع هفته</label><input className="input" type="date" value={form.week_start} onChange={(e)=>setForm({...form,week_start:e.target.value})} /></div><div className="field"><label>روز</label><select className="select" value={form.day_of_week} onChange={(e)=>setForm({...form,day_of_week:e.target.value})}>{days.map(d=><option key={d}>{d}</option>)}</select></div></div><div className="form-grid two"><div className="field"><label>شروع</label><input className="input" type="time" value={form.shift_start} onChange={(e)=>setForm({...form,shift_start:e.target.value})} /></div><div className="field"><label>پایان</label><input className="input" type="time" value={form.shift_end} onChange={(e)=>setForm({...form,shift_end:e.target.value})} /></div></div><div className="actions"><button className="btn">ذخیره</button><button type="button" className="btn ghost" onClick={()=>setEditing(null)}>انصراف</button></div></form></Modal> : null}
  </div></AppShell>;
}
