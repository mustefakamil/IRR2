import { useEffect, useState } from "react";
import { api, Project } from "../api";
import { useLang } from "../i18n";
import { EtEtcChart, KcChart, SwbChart, WaterChart } from "../components/Charts";

export function Dashboard({ project, onGoNew, onLoadSample }:
  { project: Project | null; onGoNew: () => void; onLoadSample: () => void }) {
  const { t, lang } = useLang();
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!project) { setData(null); return; }
    setLoading(true); setErr(null);
    api.dashboard(project.id).then(setData).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, [project?.id]);

  if (!project) return (
    <div className="empty-state">
      <div className="big">🌾</div>
      <p>{t("no_project")}</p>
      <div className="row" style={{ justifyContent: "center", marginTop: 14 }}>
        <button className="btn" onClick={onLoadSample}>⚡ {t("load_sample")}</button>
        <button className="btn secondary" onClick={onGoNew}>➕ {t("new_project")}</button>
      </div>
    </div>
  );

  if (loading) return <div className="spinner">{t("loading")}</div>;
  if (err) return <div className="err">{err}</div>;
  if (!data) return null;

  const s = data.summary, today = data.today, next = data.next_irrigation;
  const fmt = (n: number, d = 1) => n?.toFixed(d);

  return (
    <>
      <div className="grid cards" style={{ marginBottom: 18 }}>
        <Stat label={t("today_eto")} value={fmt(today.eto, 2)} unit="mm/day" />
        <Stat label={t("today_etc")} value={fmt(today.etc, 2)} unit="mm/day" accent />
        <Stat label={t("depletion")} value={fmt(today.ds_end, 1)} unit={`/ ${fmt(today.raw, 0)} mm RAW`} />
        <Stat label={t("next_irrigation")} value={next ? next.the_date : t("none")}
          sub={next ? `${t("rec_depth")}: ${fmt(next.dg, 1)} mm` : ""} />
        <Stat label={t("req_volume")} value={next ? fmt(next.volume_m3, 0) : t("none")} unit="m³" />
        <Stat label={t("runtime")} value={next?.runtime_hours ? fmt(next.runtime_hours, 1) : t("none")} unit="h" />
        <Stat label={t("irrigations")} value={String(s.n_irrigations)} sub={`${s.days} ${t("days_loaded")}`} />
        <Stat label={t("gross_volume")} value={fmt(s.total_gross_volume_m3, 0)} unit="m³" />
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))" }}>
        <div className="card chart-card"><h3>{t("eto_trend")}</h3><EtEtcChart trends={data.trends} /></div>
        <div className="card chart-card"><h3>{t("kc_curve")}</h3><KcChart curve={data.kc_curve} /></div>
        <div className="card chart-card"><h3>{t("swb")}</h3><SwbChart trends={data.trends} /></div>
        <div className="card chart-card"><h3>{t("water_applied")}</h3><WaterChart trends={data.trends} /></div>
      </div>
    </>
  );
}

function Stat({ label, value, unit, sub, accent }:
  { label: string; value: string; unit?: string; sub?: string; accent?: boolean }) {
  return (
    <div className={"card stat" + (accent ? " accent" : "")}>
      <div className="label">{label}</div>
      <div className="value">{value} {unit && <small>{unit}</small>}</div>
      {sub && <div className="sub">{sub}</div>}
    </div>
  );
}
