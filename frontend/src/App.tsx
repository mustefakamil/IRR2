import { useEffect, useMemo, useState, useCallback } from "react";
import { api, auth, Project } from "./api";
import { Lang, LangContext, makeT } from "./i18n";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Projects } from "./pages/Projects";
import { ProjectForm } from "./pages/ProjectForm";
import { Climate } from "./pages/Climate";
import { Schedule } from "./pages/Schedule";
import { CalendarView } from "./pages/Calendar";
import { Reports } from "./pages/Reports";
import { Crops } from "./pages/Crops";

type View = "dashboard" | "projects" | "new" | "climate" | "schedule" | "calendar" | "reports" | "crops";

const NAV: { key: View; icon: string; label: string }[] = [
  { key: "dashboard", icon: "📊", label: "dashboard" },
  { key: "projects", icon: "📁", label: "projects" },
  { key: "new", icon: "➕", label: "new_project" },
  { key: "climate", icon: "🌤️", label: "climate" },
  { key: "schedule", icon: "💧", label: "schedule" },
  { key: "calendar", icon: "📅", label: "calendar" },
  { key: "reports", icon: "📄", label: "reports" },
  { key: "crops", icon: "🌱", label: "crops_db" },
];

export function App() {
  const [lang, setLang] = useState<Lang>((localStorage.getItem("lang") as Lang) || "en");
  const [authed, setAuthed] = useState<boolean>(!!auth.token);
  const [view, setView] = useState<View>("dashboard");
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(
    Number(localStorage.getItem("pid")) || null
  );
  const [editId, setEditId] = useState<number | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const t = useMemo(() => makeT(lang), [lang]);
  const dir = lang === "ar" ? "rtl" : "ltr";

  useEffect(() => {
    document.documentElement.setAttribute("dir", dir);
    document.documentElement.setAttribute("lang", lang);
  }, [dir, lang]);

  const refreshProjects = useCallback(async () => {
    const p = await api.projects();
    setProjects(p);
    setSelectedId((cur) => (cur && p.some((x) => x.id === cur) ? cur : p[0]?.id ?? null));
  }, []);

  const [full, setFull] = useState<Project | null>(null);

  useEffect(() => { if (authed) refreshProjects(); }, [refreshProjects, authed]);
  useEffect(() => { if (selectedId) localStorage.setItem("pid", String(selectedId)); }, [selectedId]);
  // Pages need the full project (system, coordinates, salinity…), not the summary.
  useEffect(() => {
    if (authed && selectedId) api.project(selectedId).then(setFull).catch(() => setFull(null));
    else setFull(null);
  }, [authed, selectedId, projects]);

  const showToast = (m: string) => { setToast(m); setTimeout(() => setToast(null), 2600); };
  const toggle = () => { const n = lang === "en" ? "ar" : "en"; setLang(n); localStorage.setItem("lang", n); };
  const go = (v: View) => { setView(v); setMenuOpen(false); };

  const selected = projects.find((p) => p.id === selectedId) || null;

  const ctx = { lang, t, toggle };

  if (!authed) {
    return (
      <LangContext.Provider value={ctx}>
        <Login onSuccess={() => setAuthed(true)} />
      </LangContext.Provider>
    );
  }

  return (
    <LangContext.Provider value={ctx}>
      <div className="app">
        <aside className={"sidebar" + (menuOpen ? " open" : "")}>
          <div className="brand">
            <span className="logo">🌾</span>
            <div>
              <h1>{t("app_title")}</h1>
              <small>{t("app_sub")}</small>
            </div>
          </div>
          {NAV.map((n) => (
            <button key={n.key} className={"navbtn" + (view === n.key ? " active" : "")}
              onClick={() => { if (n.key === "new") setEditId(null); go(n.key); }}>
              <span className="ic">{n.icon}</span> {t(n.label)}
            </button>
          ))}
          <div className="spacer" />
          <button className="langbtn" onClick={toggle}>
            {lang === "en" ? "🇸🇦 العربية" : "🇬🇧 English"}
          </button>
          <button className="langbtn" onClick={() => auth.logout()} style={{ marginTop: 6 }}>
            🚪 {t("logout")}
          </button>
        </aside>

        <div className="main">
          <div className="topbar">
            <button className="menu-toggle" onClick={() => setMenuOpen((o) => !o)}>☰</button>
            <h2>{t(NAV.find((n) => n.key === view)!.label)}</h2>
            {selected && (
              <span className="proj-pill">
                <span>📁</span> {selected.project_name}
                <span>· {lang === "ar" ? selected.crop.name_ar : selected.crop.name_en}</span>
              </span>
            )}
          </div>

          <div className="content">
            {view === "dashboard" && (
              <Dashboard project={full}
                onGoNew={() => { setEditId(null); go("new"); }}
                onLoadSample={async () => { await api.loadSample(); await refreshProjects(); showToast("Sample project loaded"); go("dashboard"); }} />
            )}
            {view === "projects" && (
              <Projects projects={projects} selectedId={selectedId}
                onSelect={(id) => { setSelectedId(id); go("dashboard"); }}
                onEdit={(id) => { setEditId(id); go("new"); }}
                onDelete={async (id) => { await api.deleteProject(id); await refreshProjects(); showToast("Project deleted"); }}
                onLoadSample={async () => { await api.loadSample(); await refreshProjects(); showToast("Sample project loaded"); }} />
            )}
            {view === "new" && (
              <ProjectForm editId={editId}
                onSaved={async (p) => { await refreshProjects(); setSelectedId(p.id); showToast("Project saved"); go("dashboard"); }} />
            )}
            {view === "climate" && <Climate project={full} onChanged={() => showToast("Climate updated")} />}
            {view === "schedule" && <Schedule project={full} />}
            {view === "calendar" && <CalendarView project={full} />}
            {view === "reports" && <Reports project={full} />}
            {view === "crops" && <Crops />}
          </div>
        </div>
        {toast && <div className="toast">{toast}</div>}
      </div>
    </LangContext.Provider>
  );
}
