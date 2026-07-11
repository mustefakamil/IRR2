import { Project } from "../api";
import { useLang } from "../i18n";

export function Projects({ projects, selectedId, onSelect, onEdit, onDelete, onLoadSample }: {
  projects: Project[]; selectedId: number | null;
  onSelect: (id: number) => void; onEdit: (id: number) => void;
  onDelete: (id: number) => void; onLoadSample: () => void;
}) {
  const { t, lang } = useLang();

  return (
    <>
      <div className="row between" style={{ marginBottom: 16 }}>
        <span style={{ color: "var(--muted)" }}>{projects.length} {t("projects")}</span>
        <button className="btn secondary" onClick={onLoadSample}>⚡ {t("load_sample")}</button>
      </div>
      {projects.length === 0 ? (
        <div className="empty-state"><div className="big">📁</div><p>{t("no_project")}</p></div>
      ) : (
        <div className="plist">
          {projects.map((p) => (
            <div key={p.id} className={"card pcard" + (p.id === selectedId ? " selected" : "")}
              onClick={() => onSelect(p.id)}>
              <h4>{p.project_name}</h4>
              <div className="meta">
                🌱 {lang === "ar" ? p.crop.name_ar : p.crop.name_en} · 🪴 {p.soil.name_en}<br />
                📍 {p.city || "—"} · 🗓️ {p.planting_date}<br />
                📐 {p.area_value} {p.area_unit} · 💧 {p.efficiency_pct}%
              </div>
              <div className="row" style={{ marginTop: 12 }} onClick={(e) => e.stopPropagation()}>
                <button className="btn secondary" onClick={() => onSelect(p.id)}>{t("open")}</button>
                <button className="btn ghost" onClick={() => onEdit(p.id)}>{t("edit")}</button>
                <button className="btn danger" onClick={() => { if (confirm(`Delete "${p.project_name}"?`)) onDelete(p.id); }}>{t("delete")}</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
