"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import { clearAuth, getRefresh, getStoredUser, isAuthed, updateUser } from "@/lib/auth";
import type { User } from "@/lib/types";
import { Brand, Loading } from "./ui";

const employeeNav = [
  { href: "/dashboard", label: "داشبورد", icon: "🏠" },
  { href: "/attendance", label: "حضور", icon: "⏱" },
  { href: "/schedule", label: "برنامه", icon: "🗓" },
  { href: "/tasks", label: "تسک‌ها", icon: "✅" },
  { href: "/calendar", label: "تقویم", icon: "📅" }
];

const adminNav = [
  { href: "/admin", label: "داشبورد ادمین", icon: "📊" },
  { href: "/admin/members", label: "ممبرها", icon: "👥" },
  { href: "/admin/attendance", label: "ورود/خروج", icon: "⏱" },
  { href: "/admin/schedules", label: "شیفت‌ها", icon: "🗓" },
  { href: "/admin/tasks", label: "تسک‌ها", icon: "✅" },
  { href: "/admin/calendar", label: "تقویم", icon: "📅" }
];

function pageTitle(pathname: string) {
  const map: Record<string, string> = {
    "/dashboard": "داشبورد کاربر",
    "/attendance": "حضور و غیاب",
    "/schedule": "برنامه هفتگی",
    "/tasks": "مدیریت تسک‌ها",
    "/calendar": "تقویم",
    "/admin": "پنل ادمین اختصاصی",
    "/admin/members": "مدیریت ممبرها",
    "/admin/attendance": "گزارش ورود و خروج",
    "/admin/schedules": "مدیریت شیفت‌ها",
    "/admin/tasks": "مدیریت تسک‌ها",
    "/admin/calendar": "تقویم سازمانی"
  };
  return map[pathname] || "HR Portal";
}

export default function AppShell({ children, adminOnly = false }: { children: React.ReactNode; adminOnly?: boolean }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!isAuthed()) {
      router.replace("/login");
      return;
    }
    setUser(getStoredUser());
    apiFetch<User>("/auth/me/")
      .then((me) => {
        updateUser(me);
        setUser(me);
        if (adminOnly && me.role !== "admin") router.replace("/dashboard");
      })
      .catch(() => {
        clearAuth();
        router.replace("/login");
      })
      .finally(() => setChecking(false));
  }, [adminOnly, router]);

  const nav = useMemo(() => {
    if (user?.role === "admin") return pathname.startsWith("/admin") ? adminNav : [...employeeNav, { href: "/admin", label: "ادمین", icon: "⚡" }];
    return employeeNav;
  }, [pathname, user?.role]);

  async function logout() {
    const refresh = getRefresh();
    try {
      await apiFetch("/auth/logout/", { method: "POST", body: JSON.stringify({ refresh, delete_token: true }) });
    } catch {}
    clearAuth();
    router.replace("/login");
  }

  if (checking) return <Loading />;

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <Brand dark />
        <div className="nav-section">منوی اصلی</div>
        <nav className="nav-list">
          {nav.map((item) => (
            <Link className={`nav-item ${pathname === item.href ? "active" : ""}`} href={item.href} key={item.href}>
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
        {user?.role === "admin" && pathname.startsWith("/admin") ? (
          <>
            <div className="nav-section">دسترسی سریع</div>
            <nav className="nav-list">
              <Link className="nav-item" href="/dashboard"><span className="nav-icon">👤</span><span>پنل کاربر</span></Link>
            </nav>
          </>
        ) : null}
        <div className="user-mini">
          <strong>{user?.full_name || user?.username}</strong>
          <span>{user?.role === "admin" ? "مدیر سیستم" : user?.job_title || "کارمند"}</span>
          <button className="btn ghost small" style={{ width: "100%", marginTop: 12, color: "white", background: "rgba(255,255,255,.1)" }} onClick={logout}>خروج</button>
        </div>
      </aside>

      <main className="main">
        <div className="topbar">
          <div className="mobile-brand"><Brand /></div>
          <div>
            <h1>{pageTitle(pathname)}</h1>
            <p>{user?.full_name || user?.username}، خوش برگشتی 👋</p>
          </div>
          <div className="actions">
            {user?.role === "admin" && !pathname.startsWith("/admin") ? <Link className="btn secondary small" href="/admin">پنل ادمین</Link> : null}
            <button className="btn ghost small" onClick={logout}>خروج</button>
          </div>
        </div>
        {children}
      </main>

      <nav className="mobile-nav">
        {nav.slice(0, 5).map((item) => (
          <Link className={pathname === item.href ? "active" : ""} href={item.href} key={item.href}>
            <span>{item.icon}</span><span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
