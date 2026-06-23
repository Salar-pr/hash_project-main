"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ApiError, apiFetch } from "@/lib/api";
import { saveAuth } from "@/lib/auth";
import type { AuthBundle, User } from "@/lib/types";
import { Brand } from "@/components/ui";

type Pending = { status: string; detail?: string; user?: User };

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("salar");
  const [password, setPassword] = useState("12345678");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pending, setPending] = useState<Pending | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true); setError(""); setPending(null);
    try {
      const data = await apiFetch<AuthBundle>("/auth/login/", { method: "POST", auth: false, body: JSON.stringify({ username, password }) });
      saveAuth(data);
      router.replace(data.user.role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      if (err instanceof ApiError && err.status === 403 && typeof err.body === "object") {
        setPending(err.body as Pending);
      } else {
        setError(err instanceof Error ? err.message : "ورود ناموفق بود.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-card">
        <Brand />
        <h1 className="form-title">ورود به HR Portal</h1>
        <p className="form-subtitle">پنل مدرن مدیریت منابع انسانی با احراز هویت JWT و Token، هماهنگ با بک‌اند DRF.</p>
        <form className="form-grid" onSubmit={submit}>
          {pending ? <div className="alert info">حساب <b>{pending.user?.username}</b> هنوز توسط ادمین تایید نشده است. بعد از تایید، امکان ورود فعال می‌شود.</div> : null}
          {error ? <div className="alert">{error}</div> : null}
          <div className="field">
            <label>نام کاربری</label>
            <input className="input" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="مثلاً salar" autoComplete="username" />
          </div>
          <div className="field">
            <label>رمز عبور</label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 8 }}>
              <input className="input" type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="رمز عبور" autoComplete="current-password" />
              <button type="button" className="btn ghost" onClick={() => setShow((v) => !v)}>{show ? "🙈" : "👁"}</button>
            </div>
          </div>
          <button className="btn" disabled={loading || !username || !password}>{loading ? "در حال ورود..." : "ورود امن"}</button>
          <p className="footer-note">حساب نداری؟ <Link className="link" href="/register">ثبت‌نام کن</Link></p>
        </form>
      </section>

      <section className="auth-showcase">
        <Brand dark />
        <div>
          <h2 className="auth-title">کنترل کامل تیم، حضور، تسک و تقویم در یک تجربه‌ی پریمیوم</h2>
          <p className="auth-subtitle">طراحی واکنش‌گرا، سریع و مینیمال؛ الهام‌گرفته از اپ PyQt اولیه اما بازطراحی‌شده برای وب اپلیکیشن‌های مدرن.</p>
        </div>
        <div className="auth-metrics">
          <div className="auth-metric"><b>JWT</b><span>Access / Refresh</span></div>
          <div className="auth-metric"><b>Token</b><span>DRF Auth</span></div>
          <div className="auth-metric"><b>Admin</b><span>Custom Panel</span></div>
        </div>
      </section>
    </div>
  );
}
