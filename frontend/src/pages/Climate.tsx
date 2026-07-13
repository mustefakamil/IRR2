import { useEffect, useRef, useState } from "react";
import { api, Project } from "../api";
import { useLang } from "../i18n";

export function Climate({ project, onChanged }: { project: Project | null; onChanged: () => void }) {
  const { t } = useLang();
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [sources, setSources] = useState<any[]>([]);
  const [report, setReport] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = () => { if (project) api.climate(project.id).then(setRows).catch((e) => setErr(e.message)); };
  useEffect(load, [project?.id]);
  useEffect(() => {
    if (project) api.climateSources(project.id).then((s) => setSources(s.providers)).catch(() => {});
  }, [project?.id]);

  if (!project) return <div className="empty-state"><div className="big">🌤️</div><p>{t("no_project")}</p></div>;

  const mergeAll = async () => {
    setBusy(true); setErr(null); setReport(null);
    try {
      const r = await api.fetchMerged(project.id, start || undefined, end || undefined);
      setReport(r.report); load(); onChanged();
    } catch (e: any) { setErr(e.message); }
    finally { setBusy(false); }
  };

  const onUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true); setErr(null);
    try { const r = await api.uploadClimate(project.id, file, true); onChanged(); load();
      alert(`${r.inserted} rows imported. Columns: ${(r.columns_detected || []).join(", ")}`); }
    catch (e: any) { setErr(e.message); }
    finally { setBusy(false); if (fileRef.current) fileRef.current.value = ""; }
  };

  const clear = async () => {
    if (!confirm("Clear all climate data for this project?")) return;
    await api.clearClimate(project.id); load(); onChanged();
  };

  const fetchWx = async (source: string) => {
    setBusy(true); setErr(null);
    try {
      const r = await api.fetchWeather(project.id, source, start || undefined, end || undefined);
      load(); onChanged();
      alert(`${r.inserted} days imported from ${source}\n${r.start} → ${r.end}`);
    } catch (e: any) { setErr(e.message); }
    finally { setBusy(false); }
  };

  return (
    <>
      {err && <div className="err" style={{ marginBottom: 14 }}>{err}</div>}

      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ margin: "0 0 4px" }}>🛰️ {t("data_sources")}</h3>
        <p style={{ color: "var(--muted)", fontSize: 12.5, marginTop: 0 }}>
          📍 {project.city || "—"} ({project.latitude}°, {project.longitude}°) · {t("merge_desc")}
        </p>

        {/* Source status chips */}
        <div className="row" style={{ gap: 8, margin: "10px 0 14px" }}>
          {sources.map((s) => (
            <span key={s.key} className="src-chip" title={s.note}
              style={{ opacity: s.available ? 1 : 0.5 }}>
              <span className={"src-dot " + (s.available ? "on" : "off")} />
              {s.label}
              <em>{s.role === "validation" ? "validation" : "#" + s.priority}</em>
            </span>
          ))}
        </div>

        <div className="row" style={{ alignItems: "flex-end" }}>
          <div className="field"><label>{t("from_date")}</label>
            <input type="date" value={start} onChange={(e) => setStart(e.target.value)} /></div>
          <div className="field"><label>{t("to_date")}</label>
            <input type="date" value={end} onChange={(e) => setEnd(e.target.value)} /></div>
          <button className="btn" disabled={busy} onClick={mergeAll}>🔀 {t("merge_all")}</button>
        </div>
        <p style={{ color: "var(--muted)", fontSize: 12, margin: "6px 0 0" }}>{t("auto_season")}</p>

        <div className="row" style={{ gap: 8, marginTop: 8, alignItems: "center" }}>
          <span style={{ color: "var(--muted)", fontSize: 12.5 }}>{t("or_single")}</span>
          <button className="btn secondary" disabled={busy} onClick={() => fetchWx("nasa")}>🛰️ NASA POWER</button>
          <button className="btn secondary" disabled={busy} onClick={() => fetchWx("era5")}>🌐 ERA5</button>
          <button className="btn secondary" disabled={busy} onClick={() => fetchWx("open-meteo")}>🌍 Open-Meteo</button>
        </div>
        {busy && <p style={{ color: "var(--muted)", fontSize: 12.5 }}>{t("fetching")}</p>}

        {report && (
          <div className="merge-report">
            <h4>{t("merge_report")}</h4>
            <div className="row" style={{ gap: 8, marginBottom: 8 }}>
              {report.sources.map((s: any) => (
                <span key={s.key} className={"badge " + (s.status === "ok" ? "yes" : "no")}>
                  {s.key} {s.status === "ok" ? `✓ ${s.days}d` : "✕"}
                </span>
              ))}
            </div>
            <div className="table-wrap">
              <table><thead><tr><th>Parameter</th><th>{t("agreement")}</th></tr></thead>
                <tbody>
                  {Object.entries(report.parameters).map(([k, v]: any) => (
                    <tr key={k}><td style={{ textAlign: "start" }}>{k}</td>
                      <td>{v.avg_sources} / ±{v.avg_spread}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row between">
          <div>
            <h3 style={{ margin: 0 }}>{project.project_name}</h3>
            <span style={{ color: "var(--muted)", fontSize: 13 }}>{rows.length} {t("days_loaded")}</span>
          </div>
          <div className="row">
            <input ref={fileRef} type="file" accept=".csv,.xlsx,.xlsm" style={{ display: "none" }} onChange={onUpload} />
            <button className="btn" disabled={busy} onClick={() => fileRef.current?.click()}>⬆️ {t("upload_climate")}</button>
            <button className="btn danger" onClick={clear}>{t("clear_climate")}</button>
          </div>
        </div>
        <p style={{ color: "var(--muted)", fontSize: 12.5, marginBottom: 0 }}>
          CSV/Excel columns recognised: Date, Tmax, Tmin, RHmax, RHmin, RHmean, Wind, Rs (Solar), Sunshine, Rainfall.
          Missing radiation is estimated from sunshine hours (FAO-56).
        </p>
      </div>

      <div className="table-wrap">
        <table>
          <thead><tr>
            <th>Date</th><th>Jday</th><th>Tmax</th><th>Tmin</th><th>RHmax</th><th>RHmin</th>
            <th>Wind m/s</th><th>Rs MJ/m²</th><th>Rain mm</th>
          </tr></thead>
          <tbody>
            {rows.slice(0, 400).map((r) => (
              <tr key={r.id}>
                <td>{r.the_date}</td><td>{r.julian_day}</td><td>{r.tmax}</td><td>{r.tmin}</td>
                <td>{r.rh_max ?? "—"}</td><td>{r.rh_min ?? "—"}</td><td>{r.wind_speed}</td>
                <td>{r.solar_rad ?? (r.sunshine_hours ? `n=${r.sunshine_hours}` : "—")}</td><td>{r.rainfall}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {rows.length > 400 && <p style={{ color: "var(--muted)", fontSize: 12 }}>Showing first 400 of {rows.length} rows.</p>}
    </>
  );
}
