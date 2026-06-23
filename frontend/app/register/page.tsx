"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { ApiError, apiFetch } from "@/lib/api";
import { Brand } from "@/components/ui";

export default function RegisterPage() {
  const [form, setForm] = useState({ username: "", password: "", password_confirm: "", full_name: "", email: "", phone: "", job_title: "", department: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  function set<K extends keyof typeof form>(key: K, value: string) { setForm((f) => ({ ...f, [key]: value })); }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true); setError(""); setDone(false);
    try {
      await apiFetch("/auth/register/", { method: "POST", auth: false, body: JSON.stringify(form) });
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError || err instanceof Error ? err.message : "ثبت‌نام ناموفق بود.");
    } finally { setLoading(false); }
  }

  return (
    <div className="auth-page">
      <section className="auth-card">
        <Brand />
        <h1 className="form-title">ساخت حساب کاربری</h1>
        <p className="form-subtitle">بعد از ثبت‌نام، حساب شما در حالت انتظار می‌ماند تا ادمین آن را تایید کند.</p>
        <form className="form-grid" onSubmit={submit}>
          {done ? <div className="alert success">حساب ساخته شد. حالا منتظر تایید ادمین بمانید.</div> : null}
          {error ? <div className="alert">{error}</div> : null}
          <div className="form-grid two">
            <div className="field"><label>نام کاربری</label><input className="input" value={form.username} onChange={(e) => set("username", e.target.value)} /></div>
            <div className="field"><label>نام کامل</label><input className="input" value={form.full_name} onChange={(e) => set("full_name", e.target.value)} /></div>
          </div>
          <div className="form-grid two">
            <div className="field"><label>رمز عبور</label><input className="input" type="password" value={form.password} onChange={(e) => set("password", e.target.value)} /></div>
            <div className="field"><label>تکرار رمز</label><input className="input" type="password" value={form.password_confirm} onChange={(e) => set("password_confirm", e.target.value)} /></div>
          </div>
          <div className="form-grid two">
            <div className="field"><label>ایمیل</label><input className="input" value={form.email} onChange={(e) => set("email", e.target.value)} /></div>
            <div className="field"><label>تلفن</label><input className="input" value={form.phone} onChange={(e) => set("phone", e.target.value)} /></div>
          </div>
          <div className="form-grid two">
            <div className="field"><label>سمت</label><input className="input" value={form.job_title} onChange={(e) => set("job_title", e.target.value)} /></div>
            <div className="field"><label>دپارتمان</label><input className="input" value={form.department} onChange={(e) => set("department", e.target.value)} /></div>
          </div>
          <button className="btn" disabled={loading}>{loading ? "در حال ثبت..." : "ثبت‌نام"}</button>
          <p className="footer-note">قبلاً حساب ساخته‌ای؟ <Link className="link" href="/login">ورود</Link></p>
        </form>
      </section>
      <section className="auth-showcase">
        <Brand dark />
        <div>
          <h2 className="auth-title">ورود کنترل‌شده با تایید ادمین</h2>
          <p className="auth-subtitle">هر کاربر بعد از ثبت‌نام ابتدا بررسی می‌شود؛ سپس ادمین از پنل اختصاصی دسترسی او را فعال می‌کند.</p>
        </div>
        <div className="auth-metrics">
          <div className="auth-metric"><b>Pending</b><span>approval flow</span></div>
          <div className="auth-metric"><b>Secure</b><span>scrypt + HMAC</span></div>
          <div className="auth-metric"><b>Responsive</b><span>mobile ready</span></div>
        </div>
      </section>
    </div>
  );
}
