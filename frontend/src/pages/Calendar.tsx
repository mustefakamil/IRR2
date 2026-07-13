import { useEffect, useState } from "react";
import { api, ensureClimateThen, Project } from "../api";
import { useLang } from "../i18n";

const STATUS_KEYS = ["no_irrigation", "irrigation_required", "rainfall_event", "water_stress_risk", "high_et"];
const STATUS_COLOR: Record<string, string> = {
  no_irrigation: "#fff", irrigation_required: "var(--green-600)",
  rainfall_event: "#e1f0fb", water_stress_risk: "#fdeaea", high_et: "#fff6e0",
};

export function CalendarView({ project }: { project: Project | null }) {
  const { t } = useLang();
  const [events, setEvents] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [sel, setSel] = useState<any>(null);

  useEffect(() => {
    if (!project) { setEvents([]); return; }
    setErr(null);
    ensureClimateThen(project.id, () => api.calendar(project.id))
      .then((r) => setEvents(r.events)).catch((e) => setErr(e.message));
  }, [project?.id]);

  if (!project) return <div className="empty-state"><div className="big">📅</div><p>{t("no_project")}</p></div>;
  if (err) return <div className="err">{err}</div>;

  // group by month
  const byMonth: Record<string, any[]> = {};
  for (const e of events) {
    const key = e.date.slice(0, 7);
    (byMonth[key] ||= []).push(e);
  }
  const map = new Map(events.map((e) => [e.date, e]));

  return (
    <>
      <div className="legend">
        {STATUS_KEYS.map((k) => (
          <span key={k}><span className="dot" style={{ background: STATUS_COLOR[k], border: "1px solid var(--line)" }} />{t(k)}</span>
        ))}
      </div>
      {Object.entries(byMonth).map(([month, evs]) => {
        const [y, m] = month.split("-").map(Number);
        const first = new Date(y, m - 1, 1);
        const startDow = first.getDay();
        const daysInMonth = new Date(y, m, 0).getDate();
        const cells: (any | null)[] = Array(startDow).fill(null);
        for (let day = 1; day <= daysInMonth; day++) {
          const ds = `${y}-${String(m).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
          cells.push(map.get(ds) || { date: ds, status: "empty_day", day });
        }
        return (
          <div key={month}>
            <div className="mon-title">{first.toLocaleString("en", { month: "long", year: "numeric" })}</div>
            <div className="cal-grid">
              {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map((d) => <div key={d} className="cal-head">{d}</div>)}
              {cells.map((c, i) => c === null ? <div key={i} className="cal-cell empty" />
                : (
                  <div key={i} className={"cal-cell " + (c.status === "empty_day" ? "no_irrigation" : c.status)}
                    onClick={() => c.etc !== undefined && setSel(c)}>
                    <div className="dnum">{c.date.slice(-2)}</div>
                    {c.etc !== undefined && <>
                      <div>ETc {c.etc}</div>
                      {c.status === "irrigation_required" && <div>💧 {c.dg}mm</div>}
                    </>}
                  </div>
                ))}
            </div>
          </div>
        );
      })}
      {sel && (
        <div className="overlay" onClick={() => setSel(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="row between"><h3 style={{ margin: 0 }}>{sel.date}</h3>
              <button className="btn ghost" onClick={() => setSel(null)}>{t("close")}</button></div>
            <div className="kv" style={{ marginTop: 10 }}>
              <span className="k">Status</span><span className="v">{t(sel.status)}</span>
              <span className="k">Stage</span><span className="v">{sel.stage}</span>
              <span className="k">ETc</span><span className="v">{sel.etc} mm</span>
              <span className="k">Depletion (Ds end)</span><span className="v">{sel.ds_end} mm</span>
              <span className="k">RAW</span><span className="v">{sel.raw} mm</span>
              <span className="k">Gross depth Dg</span><span className="v">{sel.dg} mm</span>
              <span className="k">Volume</span><span className="v">{sel.volume_m3} m³</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
