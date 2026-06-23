"use client";

import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Empty, Loading, Modal, PageHead } from "@/components/ui";
import { apiFetch, query } from "@/lib/api";
import { addDays, faDate, mondayOf, timeOnly, toDateTimeLocal, fromDateTimeLocal } from "@/lib/date";
import type { Attendance, User } from "@/lib/types";

export default function AdminAttendancePage() {
  const [week, setWeek] = useState(mondayOf());
  const [rows, setRows] = useState<Attendance[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Attendance | null | "new">(null);
  const [form, setForm] = useState({ user: "", work_date: "", clock_in: "", clock_out: "" });
  async function load() { setLoading(true); const [r,u] = await Promise.all([apiFetch<Attendance[]>(`/admin-panel/attendance/${query({ week_start: week })}`), apiFetch<User[]>("/admin-panel/members/")]); setRows(r); setUsers(u); setLoading(false); }
  useEffect(() => { load().catch(() => setLoading(false)); }, [week]);
  function openNew() { setEditing("new"); setForm({ user: users[0]?.id ? String(users[0].id) : "", work_date: week, clock_in: "", clock_out: "" }); }
  function openEdit(r: Attendance) { const u = users.find((x) => x.username === r.username); setEditing(r); setForm({ user: String(u?.id || r.user), work_date: r.work_date, clock_in: toDateTimeLocal(r.clock_in), clock_out: toDateTimeLocal(r.clock_out) }); }
  async function save(e: FormEvent) { e.preventDefault(); const payload = { user: Number(form.user), work_date: form.work_date, clock_in: fromDateTimeLocal(form.clock_in), clock_out: fromDateTimeLocal(form.clock_out) }; if (editing === "new") await apiFetch("/admin-panel/attendance/", { method: "POST", body: JSON.stringify(payload) }); else if (editing) await apiFetch(`/admin-panel/attendance/${editing.id}/`, { method: "PATCH", body: JSON.stringify(payload) }); setEditing(null); await load(); }
  async function remove(r: Attendance) { if (confirm("حذف رکورد؟")) { await apiFetch(`/admin-panel/attendance/${r.id}/`, { method: "DELETE" }); await load(); } }
  return <AppShell adminOnly><div className="page"><PageHead title="مدیریت ورود و خروج" desc="مشاهده و اصلاح رکوردهای حضور همه ممبرها." action={<button className="btn" onClick={openNew}>＋ رکورد جدید</button>} />
    <section className="card"><div className="toolbar" style={{ marginBottom: 16 }}><button className="btn secondary" onClick={() => setWeek(addDays(week,-7))}>هفته قبل</button><input className="input" type="date" value={week} onChange={(e)=>setWeek(e.target.value)} /><button className="btn secondary" onClick={() => setWeek(addDays(week,7))}>هفته بعد</button></div>{loading ? <Loading /> : rows.length ? <div className="table-wrap"><table><thead><tr><th>کاربر</th><th>تاریخ</th><th>ورود</th><th>خروج</th><th>ساعت</th><th>عملیات</th></tr></thead><tbody>{rows.map((r)=><tr key={r.id}><td>{r.username}</td><td>{faDate(r.work_date)}</td><td>{timeOnly(r.clock_in)}</td><td>{timeOnly(r.clock_out)}</td><td>{r.hours}h</td><td><div className="actions"><button className="btn ghost small" onClick={()=>openEdit(r)}>ویرایش</button><button className="btn danger small" onClick={()=>remove(r)}>حذف</button></div></td></tr>)}</tbody></table></div> : <Empty />}</section>
    {editing ? <Modal title={editing === "new" ? "رکورد حضور جدید" : "ویرایش رکورد"} onClose={()=>setEditing(null)}><form className="form-grid" onSubmit={save}><div className="field"><label>ممبر</label><select className="select" value={form.user} onChange={(e)=>setForm({...form,user:e.target.value})}>{users.map((u)=><option key={u.id} value={u.id}>{u.full_name || u.username}</option>)}</select></div><div className="field"><label>تاریخ</label><input className="input" type="date" value={form.work_date} onChange={(e)=>setForm({...form,work_date:e.target.value})} /></div><div className="form-grid two"><div className="field"><label>ورود</label><input className="input" type="datetime-local" value={form.clock_in} onChange={(e)=>setForm({...form,clock_in:e.target.value})} /></div><div className="field"><label>خروج</label><input className="input" type="datetime-local" value={form.clock_out} onChange={(e)=>setForm({...form,clock_out:e.target.value})} /></div></div><div className="actions"><button className="btn">ذخیره</button><button type="button" className="btn ghost" onClick={()=>setEditing(null)}>انصراف</button></div></form></Modal> : null}
  </div></AppShell>;
}
