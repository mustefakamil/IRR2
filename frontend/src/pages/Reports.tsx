import { useEffect, useState } from "react";
import { api, ensureClimateThen, Project, Summary } from "../api";
import { useLang } from "../i18n";
import { EtcAetiBars, EtcAetiCumulative } from "../components/Charts";

export function Reports({ project }: { project: Project | null }) {
  const { t, lang } = useLang();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [val, setVal] = useState<any>(null);
  const [validating, setValidating] = useState(false);
  const [level, setLevel] = useState("L2");

  useEffect(() => {
    if (!project) { setSummary(null); return; }
    setVal(null); setErr(null);
    ensureClimateThen(project.id, () => api.schedule(project.id))
      .then((r) => setSummary(r.summary)).catch((e) => setErr(e.message));
  }, [project?.id]);

  const runValidation = async () => {
    if (!project) return;
    setValidating(true); setErr(null); setVal(null);
    try { setVal(await api.validate(project.id, level)); }
    catch (e: any) { setErr(e.message); }
    finally { setValidating(false); }
  };

  if (!project) return <div className="empty-state"><div className="big">📄</div><p>{t("no_project")}</p></div>;

  const c = project.crop, s = project.soil, sy = project.system;
  const info: [string, any][] = [
    [t("project_name"), project.project_name], [t("farm_name"), project.farm_name || "—"],
    [t("field_name"), project.field_name || "—"],
    [t("city"), `${project.city || "—"}, ${project.region || ""} ${project.country || ""}`],
    [`${t("latitude")} / ${t("longitude")}`, `${project.latitude} / ${project.longitude}`],
    [t("elevation"), `${project.elevation} m`],
    [t("area"), `${project.area_value} ${project.area_unit}`],
    [t("planting_date"), project.planting_date],
    [t("crop"), lang === "ar" ? c.name_ar : `${c.name_en} (${c.scientific_name})`],
    [t("soil"), `${s.name_en} — FC ${s.theta_fc}, WP ${s.theta_wp}`],
    [t("system"), `${sy.name_en} @ ${project.efficiency_pct}%`],
    ["ECw / ECe", `${project.ecw} / ${project.ece} dS/m`],
  ];

  return (
    <>
      {err && <div className="err" style={{ marginBottom: 14 }}>{err}</div>}
      <div className="row" style={{ marginBottom: 18 }}>
        <button className="btn danger" onClick={() => api.downloadPdf(project.id).catch((e) => setErr(e.message))}>📄 {t("download_pdf")}</button>
        <button className="btn" onClick={() => api.downloadExcel(project.id).catch((e) => setErr(e.message))}>⬇️ {t("download_excel")}</button>
        <button className="btn secondary" onClick={() => api.downloadCsv(project.id).catch((e) => setErr(e.message))}>⬇️ {t("download_csv")}</button>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))" }}>
        <div className="card">
          <h3>📋 Project Information</h3>
          <div className="kv">
            {info.map(([k, v]) => <div key={k} style={{ display: "contents" }}>
              <span className="k">{k}</span><span className="v">{v}</span></div>)}
          </div>
        </div>

        <div className="card">
          <h3>🌱 Crop Parameters (FAO-56)</h3>
          <div className="kv">
            <span className="k">Stages Lini/Ldev/Lmid/Llate</span><span className="v">{c.l_ini}/{c.l_dev}/{c.l_mid}/{c.l_late} d</span>
            <span className="k">Kc ini / mid / end</span><span className="v">{c.kc_ini} / {c.kc_mid} / {c.kc_end}</span>
            <span className="k">Root depth Zr</span><span className="v">{c.zr_min}–{c.zr_max} m</span>
            <span className="k">Depletion fraction p</span><span className="v">{c.p}</span>
            <span className="k">Yield response Ky</span><span className="v">{c.ky}</span>
            <span className="k">Source</span><span className="v"><span className={"pill " + c.source}>{c.source}</span></span>
          </div>
        </div>

        {summary && (
          <div className="card">
            <h3>💧 Water Requirement Summary</h3>
            <div className="kv">
              <span className="k">Season length</span><span className="v">{summary.days} days</span>
              <span className="k">Number of irrigations</span><span className="v">{summary.n_irrigations}</span>
              <span className="k">Total ETo</span><span className="v">{summary.total_eto} mm</span>
              <span className="k">Total ETc (crop water req.)</span><span className="v">{summary.total_etc} mm</span>
              <span className="k">Effective rainfall</span><span className="v">{summary.total_effective_rain} mm</span>
              <span className="k">Net irrigation depth</span><span className="v">{summary.total_net_depth} mm</span>
              <span className="k">Gross irrigation depth</span><span className="v">{summary.total_gross_depth} mm</span>
              <span className="k">Net water volume</span><span className="v">{summary.total_net_volume_m3} m³</span>
              <span className="k">Gross water volume</span><span className="v">{summary.total_gross_volume_m3} m³</span>
              <span className="k">Total pump runtime</span><span className="v">{summary.total_runtime_hours} h</span>
            </div>
          </div>
        )}

        <div className="card">
          <h3>📐 FAO-56 Methodology</h3>
          <div className="formula-box">ETo = FAO-56 Penman-Monteith (Eq. 6)</div>
          <div className="formula-box">ETc = Kc × ETo</div>
          <div className="formula-box">TAW = 1000·(θFC−θWP)·Zr &nbsp; RAW = p·TAW</div>
          <div className="formula-box">Irrigate when Dr ≥ RAW &nbsp;·&nbsp; Dg = Dn / ((1−LR)·Ea)</div>
          <p style={{ color: "var(--muted)", fontSize: 12 }}>
            Engineering note: reference ET uses the canonical FAO-56 constants (γ=0.000665·P, albedo 0.23,
            σ=4.903×10⁻⁹). All defaults are user-editable.
          </p>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="row between" style={{ marginBottom: 6 }}>
          <h3 style={{ margin: 0 }}>🛰️ {t("validation")}</h3>
          <div className="row" style={{ gap: 8 }}>
            <select value={level} onChange={(e) => setLevel(e.target.value)}
              style={{ padding: "9px 11px", borderRadius: 8, border: "1px solid var(--line)" }}>
              <option value="L2">WaPOR L2 — 100 m</option>
              <option value="L1">WaPOR L1 — 300 m</option>
            </select>
            <button className="btn" onClick={runValidation} disabled={validating}>
              {validating ? "…" : "✔️ " + t("run_validation")}
            </button>
          </div>
        </div>
        <p style={{ color: "var(--muted)", fontSize: 12.5, marginTop: 0 }}>{t("validation_desc")}</p>
        {validating && <p style={{ color: "var(--muted)", fontSize: 13 }}>{t("validating")}</p>}
        {val && (
          <>
            <div className="grid cards" style={{ marginTop: 6 }}>
              <div className="card stat"><div className="label">{t("computed_etc")}</div>
                <div className="value" style={{ fontSize: 24 }}>{val.computed.seasonal_etc_mm}<small> mm</small></div></div>
              {val.wapor.actual_et_mm != null ? (
                <>
                  <div className="card stat accent"><div className="label">{t("wapor_aeti")}</div>
                    <div className="value" style={{ fontSize: 24 }}>{val.wapor.actual_et_mm}<small> mm</small></div></div>
                  <div className="card stat"><div className="label">{t("aeti_ratio")}</div>
                    <div className="value" style={{ fontSize: 24 }}>{val.wapor.ratio_aeti_over_etc}</div></div>
                  <div className="card stat"><div className="label">{t("coverage")}</div>
                    <div className="value" style={{ fontSize: 24 }}>{val.wapor.dekads_found}/{val.wapor.dekads_expected}<small> dekads</small></div>
                    <div className="sub">{val.wapor.window?.start} → {val.wapor.window?.end}</div></div>
                </>
              ) : (
                <div className="card" style={{ gridColumn: "span 2" }}>
                  <div className="err">{val.wapor.message || "WaPOR unavailable"}</div>
                </div>
              )}
            </div>
            {val.wapor.series && val.wapor.series.length > 0 && (
              <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", marginTop: 16 }}>
                <div className="card chart-card"><h3>📊 {t("per_dekad")}</h3>
                  <EtcAetiBars series={val.wapor.series} /></div>
                <div className="card chart-card"><h3>📈 {t("cumulative")}</h3>
                  <EtcAetiCumulative series={val.wapor.series} /></div>
              </div>
            )}
            {val.wapor.note && (
              <p style={{ color: "var(--muted)", fontSize: 12, marginTop: 10 }}>ℹ️ {val.wapor.note}</p>
            )}
            {val.wapor.resolution && (
              <p style={{ color: "var(--muted)", fontSize: 11.5, marginTop: 2 }}>Source: FAO WaPOR {val.wapor.resolution}</p>
            )}
          </>
        )}
      </div>
    </>
  );
}
