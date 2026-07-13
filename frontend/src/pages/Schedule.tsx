import { useEffect, useState } from "react";
import { api, ensureClimateThen, Project, DailyRow, Summary } from "../api";
import { useLang } from "../i18n";

export function Schedule({ project }: { project: Project | null }) {
  const { t } = useLang();
  const [daily, setDaily] = useState<DailyRow[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [provisioning, setProvisioning] = useState(false);
  const [detailDate, setDetailDate] = useState<string | null>(null);

  useEffect(() => {
    if (!project) { setDaily([]); return; }
    setLoading(true); setErr(null); setProvisioning(false);
    ensureClimateThen(project.id, () => api.schedule(project.id), () => setProvisioning(true))
      .then((r) => { setDaily(r.daily); setSummary(r.summary); })
      .catch((e) => setErr(e.message))
      .finally(() => { setLoading(false); setProvisioning(false); });
  }, [project?.id]);

  if (!project) return <div className="empty-state"><div className="big">💧</div><p>{t("no_project")}</p></div>;
  if (loading) return <div className="spinner">{provisioning ? t("provisioning") : t("loading")}</div>;
  if (err) return <div className="err">{err}</div>;

  const cols = ["Day", "Date", "Jday", "Stage", "ETo", "Kc", "ETc", "Rain", "Pe", "LR", "IWR",
    "Zr", "TAW", "RAW", "p", "Ds beg", "Use", "Ds end", "Irr", "Dn", "Dg", "Vol m³", "RT h"];

  return (
    <>
      {summary && (
        <div className="grid cards" style={{ marginBottom: 16 }}>
          <Mini label="ETo" v={summary.total_eto} u="mm" />
          <Mini label="ETc" v={summary.total_etc} u="mm" />
          <Mini label={t("irrigations")} v={summary.n_irrigations} />
          <Mini label="Gross depth" v={summary.total_gross_depth} u="mm" />
          <Mini label="Gross volume" v={summary.total_gross_volume_m3} u="m³" />
          <Mini label={t("runtime")} v={summary.total_runtime_hours} u="h" />
        </div>
      )}
      <div className="table-wrap">
        <table>
          <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>
            {daily.map((r) => (
              <tr key={r.day} className={r.irrigate ? "irr" : ""}>
                <td>{r.day}</td>
                <td className="clickable" onClick={() => setDetailDate(r.the_date)}>{r.the_date}</td>
                <td>{r.julian_day}</td><td>{r.stage}</td>
                <td>{r.eto}</td><td>{r.kc}</td><td>{r.etc}</td>
                <td>{r.rainfall}</td><td>{r.pe}</td><td>{r.lr}</td><td>{r.iwr}</td>
                <td>{r.root_depth}</td><td>{r.taw}</td><td>{r.raw}</td><td>{r.p}</td>
                <td>{r.ds_begin}</td><td>{r.daily_water_use}</td><td>{r.ds_end}</td>
                <td>{r.irrigate ? <span className="badge yes">YES</span> : <span className="badge no">no</span>}</td>
                <td>{r.dn || ""}</td><td>{r.dg || ""}</td><td>{r.volume_m3 || ""}</td>
                <td>{r.runtime_hours ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p style={{ color: "var(--muted)", fontSize: 12 }}>💡 Click any date to see the full FAO-56 ETo calculation.</p>
      {detailDate && project && <EtoModal projectId={project.id} date={detailDate} onClose={() => setDetailDate(null)} />}
    </>
  );
}

function Mini({ label, v, u }: { label: string; v: number; u?: string }) {
  return <div className="card stat"><div className="label">{label}</div>
    <div className="value" style={{ fontSize: 22 }}>{v}{u && <small> {u}</small>}</div></div>;
}

function EtoModal({ projectId, date, onClose }: { projectId: number; date: string; onClose: () => void }) {
  const { t } = useLang();
  const [d, setD] = useState<any>(null);
  useEffect(() => { api.etoDetail(projectId, date).then(setD).catch(() => setD({ error: true })); }, [projectId, date]);

  const rows: [string, string, number][] = d && !d.error ? [
    ["Tmean", "°C", d.tmean], ["e°(Tmax)", "kPa", d.e_tmax], ["e°(Tmin)", "kPa", d.e_tmin],
    ["es (sat. vapour)", "kPa", d.es], ["ea (actual vapour)", "kPa", d.ea], ["VPD (es−ea)", "kPa", d.vpd],
    ["Δ slope", "kPa/°C", d.delta], ["P pressure", "kPa", d.pressure], ["γ psychrometric", "kPa/°C", d.gamma],
    ["dr (Earth-Sun)", "", d.dr], ["δ declination", "rad", d.decl], ["ωs sunset angle", "rad", d.sunset_angle],
    ["N daylight", "h", d.daylight_hours], ["Ra extraterr.", "MJ/m²/d", d.ra], ["Rs solar", "MJ/m²/d", d.rs],
    ["Rso clear-sky", "MJ/m²/d", d.rso], ["Rns net short", "MJ/m²/d", d.rns], ["Rnl net long", "MJ/m²/d", d.rnl],
    ["Rn net radiation", "MJ/m²/d", d.rn], ["u2 wind @2m", "m/s", d.u2],
  ] : [];

  return (
    <div className="overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="row between"><h3 style={{ margin: 0 }}>{t("formula_eto")} — {date}</h3>
          <button className="btn ghost" onClick={onClose}>{t("close")}</button></div>
        {!d && <div className="spinner">{t("loading")}</div>}
        {d?.error && <div className="err">No climate for this date.</div>}
        {d && !d.error && (
          <>
            <div className="formula-box">
              ETo = [0.408·Δ·(Rn−G) + γ·(900/(T+273))·u₂·(es−ea)] / [Δ + γ·(1+0.34·u₂)]<br />
              <b>ETo = {d.eto?.toFixed(3)} mm/day</b>
            </div>
            <div className="section-title">{t("intermediate")}</div>
            <div className="kv">
              {rows.map(([k, u, v]) => (
                <div key={k} style={{ display: "contents" }}>
                  <span className="k">{k}</span>
                  <span className="v">{typeof v === "number" ? v.toFixed(4) : "—"} {u}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
