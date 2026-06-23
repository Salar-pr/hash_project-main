"use client";

import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Empty, Loading, Modal, PageHead } from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { faDate } from "@/lib/date";
import type { Task, User } from "@/lib/types";

export default function AdminTasksPage() {
  const [rows, setRows] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Task | null | "new">(null);
  const [form, setForm] = useState({ title: "", description: "", assigned_to: "", status: "todo", priority: "medium", due_date: "" });
  async function load() { setLoading(true); const [r,u] = await Promise.all([apiFetch<Task[]>("/admin-panel/tasks/"), apiFetch<User[]>("/admin-panel/members/")]); setRows(r); setUsers(u); setLoading(false); }
  useEffect(() => { load().catch(() => setLoading(false)); }, []);
  function openNew() { setEditing("new"); setForm({ title: "", description: "", assigned_to: users[0]?.id ? String(users[0].id) : "", status: "todo", priority: "medium", due_date: "" }); }
  function openEdit(t: Task) { setEditing(t); setForm({ title: t.title, description: t.description || "", assigned_to: String(t.assigned_to), status: t.status, priority: t.priority, due_date: t.due_date || "" }); }
  async function save(e: FormEvent) { e.preventDefault(); const payload = { ...form, assigned_to: Number(form.assigned_to), due_date: form.due_date || null }; if (editing === "new") await apiFetch("/admin-panel/tasks/", { method: "POST", body: JSON.stringify(payload) }); else if (editing) await apiFetch(`/admin-panel/tasks/${editing.id}/`, { method: "PATCH", body: JSON.stringify(payload) }); setEditing(null); await load(); }
  async function remove(t: Task) { if (confirm("حذف تسک؟")) { await apiFetch(`/admin-panel/tasks/${t.id}/`, { method: "DELETE" }); await load(); } }
  return <AppShell adminOnly><div className="page"><PageHead title="مدیریت تسک‌ها" desc="ایجاد، ویرایش، حذف و پیگیری وضعیت تسک‌های ممبرها." action={<button className="btn" onClick={openNew}>＋ تسک جدید</button>} />
    <section className="card">{loading ? <Loading /> : rows.length ? <div className="table-wrap"><table><thead><tr><th>عنوان</th><th>ممبر</th><th>وضعیت</th><th>اولویت</th><th>مهلت</th><th>عملیات</th></tr></thead><tbody>{rows.map((t)=><tr key={t.id}><td>{t.title}</td><td>{t.assigned_to_full_name || t.assigned_to_username}</td><td><Badge tone={t.status === "done" ? "success" : t.status === "in_progress" ? "info" : "warning"}>{t.status}</Badge></td><td>{t.priority}</td><td>{faDate(t.due_date)}</td><td><div className="actions"><button className="btn ghost small" onClick={()=>openEdit(t)}>ویرایش</button><button className="btn danger small" onClick={()=>remove(t)}>حذف</button></div></td></tr>)}</tbody></table></div> : <Empty />}</section>
    {editing ? <Modal title={editing === "new" ? "تسک جدید" : "ویرایش تسک"} onClose={()=>setEditing(null)}><form className="form-grid" onSubmit={save}><div className="field"><label>عنوان</label><input className="input" value={form.title} onChange={(e)=>setForm({...form,title:e.target.value})} /></div><div className="field"><label>توضیحات</label><textarea className="textarea" value={form.description} onChange={(e)=>setForm({...form,description:e.target.value})} /></div><div className="field"><label>ممبر</label><select className="select" value={form.assigned_to} onChange={(e)=>setForm({...form,assigned_to:e.target.value})}>{users.map((u)=><option key={u.id} value={u.id}>{u.full_name || u.username}</option>)}</select></div><div className="form-grid three"><div className="field"><label>وضعیت</label><select className="select" value={form.status} onChange={(e)=>setForm({...form,status:e.target.value})}><option value="todo">todo</option><option value="in_progress">in_progress</option><option value="done">done</option><option value="cancelled">cancelled</option></select></div><div className="field"><label>اولویت</label><select className="select" value={form.priority} onChange={(e)=>setForm({...form,priority:e.target.value})}><option value="low">low</option><option value="medium">medium</option><option value="high">high</option><option value="urgent">urgent</option></select></div><div className="field"><label>مهلت</label><input className="input" type="date" value={form.due_date} onChange={(e)=>setForm({...form,due_date:e.target.value})} /></div></div><div className="actions"><button className="btn">ذخیره</button><button type="button" className="btn ghost" onClick={()=>setEditing(null)}>انصراف</button></div></form></Modal> : null}
  </div></AppShell>;
}
