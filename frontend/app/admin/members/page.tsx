"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { Badge, Empty, Loading, Modal, PageHead } from "@/components/ui";
import { apiFetch, query } from "@/lib/api";
import { faDateTime } from "@/lib/date";
import type { User } from "@/lib/types";

const emptyForm = { username: "", password: "", full_name: "", email: "", phone: "", job_title: "", department: "", salary_ruble: "", role: "employee", is_active: true, is_approved: true };

export default function AdminMembersPage() {
  const [rows, setRows] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [approved, setApproved] = useState("");
  const [editing, setEditing] = useState<User | null | "new">(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");

  async function load() {
    setLoading(true);
    setRows(await apiFetch<User[]>(`/admin-panel/members/${query({ search, approved })}`));
    setLoading(false);
  }
  useEffect(() => { load().catch(() => setLoading(false)); }, [search, approved]);

  function openNew() { setEditing("new"); setForm(emptyForm); setError(""); }
  function openEdit(u: User) { setEditing(u); setError(""); setForm({ username: u.username, password: "", full_name: u.full_name || "", email: u.email || "", phone: u.phone || "", job_title: u.job_title || "", department: u.department || "", salary_ruble: String(u.salary_ruble || ""), role: u.role, is_active: u.is_active, is_approved: u.is_approved }); }
  function set<K extends keyof typeof form>(key: K, value: any) { setForm((f) => ({ ...f, [key]: value })); }

  async function save(e: FormEvent) {
    e.preventDefault(); setError("");
    const payload: any = { ...form, salary_ruble: form.salary_ruble || null };
    if (!payload.password) delete payload.password;
    try {
      if (editing === "new") await apiFetch("/admin-panel/members/", { method: "POST", body: JSON.stringify(payload) });
      else if (editing) await apiFetch(`/admin-panel/members/${editing.id}/`, { method: "PATCH", body: JSON.stringify(payload) });
      setEditing(null); await load();
    } catch (e) { setError(e instanceof Error ? e.message : "خطا در ذخیره"); }
  }
  async function remove(u: User) { if (confirm(`حذف ${u.username}؟`)) { await apiFetch(`/admin-panel/members/${u.id}/`, { method: "DELETE" }); await load(); } }
  async function approve(u: User) { await apiFetch(`/admin-panel/members/${u.id}/approve/`, { method: "POST" }); await load(); }
  async function reject(u: User) { await apiFetch(`/admin-panel/members/${u.id}/reject/`, { method: "POST" }); await load(); }

  return (
    <AppShell adminOnly>
      <div className="page">
        <PageHead title="مدیریت ممبرها" desc="نمایش کامل اطلاعات، روبل، نقش، وضعیت تایید و عملیات حذف/افزودن/تغییر." action={<button className="btn" onClick={openNew}>＋ ممبر جدید</button>} />
        <section className="card">
          <div className="toolbar" style={{ marginBottom: 16 }}>
            <input className="input" placeholder="جستجو..." value={search} onChange={(e) => setSearch(e.target.value)} />
            <select className="select" value={approved} onChange={(e) => setApproved(e.target.value)}><option value="">همه وضعیت‌ها</option><option value="true">تایید شده</option><option value="false">در انتظار</option></select>
          </div>
          {loading ? <Loading /> : rows.length ? <div className="table-wrap"><table><thead><tr><th>نام کاربری</th><th>نام</th><th>سمت</th><th>حقوق روبل</th><th>نقش</th><th>تایید</th><th>ثبت</th><th>عملیات</th></tr></thead><tbody>{rows.map((u) => <tr key={u.id}><td>{u.username}</td><td>{u.full_name || "—"}</td><td>{u.job_title || "—"}</td><td>{u.salary_ruble ? `${u.salary_ruble} ₽` : "—"}</td><td><Badge tone={u.role === "admin" ? "primary" : "neutral"}>{u.role}</Badge></td><td><Badge tone={u.is_approved ? "success" : "warning"}>{u.is_approved ? "تایید" : "منتظر"}</Badge></td><td>{faDateTime(u.created_at)}</td><td><div className="actions"><Link className="btn secondary small" href={`/admin/members/${u.id}`}>جزئیات</Link><button className="btn ghost small" onClick={() => openEdit(u)}>ویرایش</button>{u.is_approved ? <button className="btn warning small" onClick={() => reject(u)}>تعلیق</button> : <button className="btn success small" onClick={() => approve(u)}>تایید</button>}<button className="btn danger small" onClick={() => remove(u)}>حذف</button></div></td></tr>)}</tbody></table></div> : <Empty />}
        </section>
      </div>
      {editing ? <Modal title={editing === "new" ? "افزودن ممبر" : `ویرایش ${editing.username}`} onClose={() => setEditing(null)}>
        <form className="form-grid" onSubmit={save}>
          {error ? <div className="alert">{error}</div> : null}
          <div className="form-grid two"><div className="field"><label>نام کاربری</label><input className="input" value={form.username} onChange={(e) => set("username", e.target.value)} /></div><div className="field"><label>رمز عبور {editing !== "new" ? "جدید" : ""}</label><input className="input" type="password" value={form.password} onChange={(e) => set("password", e.target.value)} placeholder={editing === "new" ? "پیش‌فرض 12345678 در صورت خالی" : "خالی بماند تغییر نمی‌کند"} /></div></div>
          <div className="form-grid two"><div className="field"><label>نام کامل</label><input className="input" value={form.full_name} onChange={(e) => set("full_name", e.target.value)} /></div><div className="field"><label>ایمیل</label><input className="input" value={form.email} onChange={(e) => set("email", e.target.value)} /></div></div>
          <div className="form-grid two"><div className="field"><label>تلفن</label><input className="input" value={form.phone} onChange={(e) => set("phone", e.target.value)} /></div><div className="field"><label>حقوق روبل</label><input className="input" type="number" value={form.salary_ruble} onChange={(e) => set("salary_ruble", e.target.value)} /></div></div>
          <div className="form-grid two"><div className="field"><label>سمت</label><input className="input" value={form.job_title} onChange={(e) => set("job_title", e.target.value)} /></div><div className="field"><label>دپارتمان</label><input className="input" value={form.department} onChange={(e) => set("department", e.target.value)} /></div></div>
          <div className="form-grid two"><div className="field"><label>نقش</label><select className="select" value={form.role} onChange={(e) => set("role", e.target.value)}><option value="employee">employee</option><option value="admin">admin</option></select></div><div className="field"><label>وضعیت</label><select className="select" value={String(form.is_approved)} onChange={(e) => set("is_approved", e.target.value === "true")}><option value="true">تایید شده</option><option value="false">در انتظار</option></select></div></div>
          <div className="actions"><button className="btn">ذخیره</button><button type="button" className="btn ghost" onClick={() => setEditing(null)}>انصراف</button></div>
        </form>
      </Modal> : null}
    </AppShell>
  );
}
