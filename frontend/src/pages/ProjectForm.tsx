import { useEffect, useMemo, useState } from "react";
import { api, Crop, Soil, System, City, Project } from "../api";
import { useLang } from "../i18n";

const empty = {
  project_name: "", farm_name: "", field_name: "", country: "Saudi Arabia", region: "", city: "",
  latitude: 24.0, longitude: 46.7, elevation: 600, wind_height: 2,
  area_value: 1, area_unit: "ha", planting_date: new Date().toISOString().slice(0, 10),
  crop_id: 0, soil_id: 0, system_id: 0, efficiency_pct: 90, ecw: 0, ece: 0,
  strategy_mode: "refill", deficit_fraction: 1, rainfall_method: "usda_scs",
  n_emitters: 0, emitter_flow_lph: 4,
};

export function ProjectForm({ editId, onSaved }:
  { editId: number | null; onSaved: (p: Project) => void }) {
  const { t, lang } = useLang();
  const [f, setF] = useState<any>(empty);
  const [crops, setCrops] = useState<Crop[]>([]);
  const [soils, setSoils] = useState<Soil[]>([]);
  const [systems, setSystems] = useState<System[]>([]);
  const [cities, setCities] = useState<City[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([api.crops(), api.soils(), api.systems(), api.cities()]).then(([c, s, sy, ct]) => {
      setCrops(c); setSoils(s); setSystems(sy); setCities(ct);
      setF((prev: any) => ({ ...prev, crop_id: prev.crop_id || c[0]?.id, soil_id: prev.soil_id || s[0]?.id, system_id: prev.system_id || sy[0]?.id }));
    });
  }, []);

  const regions = useMemo(
    () => Array.from(new Set(cities.map((c) => c.region))).sort(), [cities]);
  const citiesInRegion = useMemo(
    () => cities.filter((c) => c.region === f.region), [cities, f.region]);

  const onRegion = (region: string) => set("region", region);
  const onCity = (name: string) => {
    const city = cities.find((c) => c.name_en === name && c.region === f.region);
    if (city) {
      setF((prev: any) => ({
        ...prev, city: city.name_en, region: city.region, country: city.country,
        latitude: city.latitude, longitude: city.longitude, elevation: city.elevation,
      }));
    } else {
      set("city", name);
    }
  };

  useEffect(() => {
    if (editId) api.project(editId).then((p) => setF({ ...p }));
    else setF({ ...empty });
  }, [editId]);

  const set = (k: string, v: any) => setF((prev: any) => ({ ...prev, [k]: v }));

  const onCrop = (id: number) => set("crop_id", id);
  const onSystem = (id: number) => {
    set("system_id", id);
    const sys = systems.find((s) => s.id === id);
    if (sys) set("efficiency_pct", sys.default_efficiency_pct);
  };

  const submit = async () => {
    setErr(null);
    if (!f.project_name.trim()) { setErr("Project name is required"); return; }
    setSaving(true);
    try {
      const body = { ...f, latitude: +f.latitude, longitude: +f.longitude, elevation: +f.elevation,
        area_value: +f.area_value, efficiency_pct: +f.efficiency_pct, ecw: +f.ecw, ece: +f.ece,
        n_emitters: +f.n_emitters, emitter_flow_lph: +f.emitter_flow_lph, deficit_fraction: +f.deficit_fraction };
      const p = editId ? await api.updateProject(editId, body) : await api.createProject(body);
      // Provision climate for the selected city/season so the schedule is ready.
      try { await api.autoClimate(p.id); } catch (e: any) {
        setErr("Project saved, but climate provisioning failed: " + e.message);
      }
      onSaved(p);
    } catch (e: any) { setErr(e.message); } finally { setSaving(false); }
  };

  const nm = (o: { name_en: string; name_ar: string }) => (lang === "ar" ? o.name_ar || o.name_en : o.name_en);

  return (
    <div className="card">
      {err && <div className="err" style={{ marginBottom: 14 }}>{err}</div>}

      <div className="section-title">{t("project_name")}</div>
      <div className="form-grid">
        <Field label={t("project_name")}><input value={f.project_name} onChange={(e) => set("project_name", e.target.value)} /></Field>
        <Field label={t("farm_name")}><input value={f.farm_name} onChange={(e) => set("farm_name", e.target.value)} /></Field>
        <Field label={t("field_name")}><input value={f.field_name} onChange={(e) => set("field_name", e.target.value)} /></Field>
      </div>

      <div className="section-title">📍 {t("region_sel")}</div>
      <div className="form-grid">
        <Field label={t("country")}><input value={f.country} onChange={(e) => set("country", e.target.value)} /></Field>
        <Field label={t("region_sel")}>
          <select value={f.region} onChange={(e) => onRegion(e.target.value)}>
            <option value="">—</option>
            {regions.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </Field>
        <Field label={t("city_sel")}>
          <select value={f.city} onChange={(e) => onCity(e.target.value)} disabled={!f.region}>
            <option value="">—</option>
            {citiesInRegion.map((c) => (
              <option key={c.id} value={c.name_en}>
                {lang === "ar" ? c.name_ar : c.name_en}
              </option>
            ))}
          </select>
        </Field>
      </div>
      <p style={{ color: "var(--muted)", fontSize: 12, margin: "2px 0 0" }}>
        ℹ️ {t("auto_coords")}
        {f.city && ` (${f.latitude}°, ${f.longitude}°, ${f.elevation} m)`}
      </p>

      <div className="section-title">📐 {t("area")}</div>
      <div className="form-grid">
        <Field label={t("area")}><input type="number" step="0.01" value={f.area_value} onChange={(e) => set("area_value", e.target.value)} /></Field>
        <Field label="Unit">
          <select value={f.area_unit} onChange={(e) => set("area_unit", e.target.value)}>
            <option value="ha">ha</option><option value="m2">m²</option><option value="acre">acre</option>
          </select>
        </Field>
        <Field label={t("planting_date")}><input type="date" value={f.planting_date} onChange={(e) => set("planting_date", e.target.value)} /></Field>
      </div>

      <div className="section-title">🌱 {t("crop")} / {t("soil")} / {t("system")}</div>
      <div className="form-grid">
        <Field label={t("crop")}>
          <select value={f.crop_id} onChange={(e) => onCrop(+e.target.value)}>
            {crops.map((c) => <option key={c.id} value={c.id}>{nm(c)} ({c.category})</option>)}
          </select>
        </Field>
        <Field label={t("soil")}>
          <select value={f.soil_id} onChange={(e) => set("soil_id", +e.target.value)}>
            {soils.map((s) => <option key={s.id} value={s.id}>{nm(s)}</option>)}
          </select>
        </Field>
        <Field label={t("system")}>
          <select value={f.system_id} onChange={(e) => onSystem(+e.target.value)}>
            {systems.map((s) => <option key={s.id} value={s.id}>{nm(s)}</option>)}
          </select>
        </Field>
        <Field label={t("efficiency")}><input type="number" value={f.efficiency_pct} onChange={(e) => set("efficiency_pct", e.target.value)} /></Field>
        <Field label={t("ecw")}><input type="number" step="0.1" value={f.ecw} onChange={(e) => set("ecw", e.target.value)} /></Field>
        <Field label={t("ece")}><input type="number" step="0.1" value={f.ece} onChange={(e) => set("ece", e.target.value)} /></Field>
      </div>

      <div className="section-title">💧 {t("strategy")}</div>
      <div className="form-grid">
        <Field label={t("strategy")}>
          <select value={f.strategy_mode} onChange={(e) => set("strategy_mode", e.target.value)}>
            <option value="refill">{t("full")}</option>
            <option value="mad">{t("mad")}</option>
            <option value="deficit">{t("deficit")}</option>
          </select>
        </Field>
        {f.strategy_mode === "deficit" && (
          <Field label="Deficit fraction (0-1)"><input type="number" step="0.05" min="0.1" max="1" value={f.deficit_fraction} onChange={(e) => set("deficit_fraction", e.target.value)} /></Field>
        )}
        <Field label={t("rainfall_method")}>
          <select value={f.rainfall_method} onChange={(e) => set("rainfall_method", e.target.value)}>
            <option value="usda_scs">USDA-SCS</option>
            <option value="fao">FAO</option>
            <option value="fixed">Fixed %</option>
            <option value="manual">Manual</option>
          </select>
        </Field>
        <Field label={t("n_emitters")}><input type="number" value={f.n_emitters} onChange={(e) => set("n_emitters", e.target.value)} /></Field>
        <Field label={t("emitter_flow")}><input type="number" step="0.1" value={f.emitter_flow_lph} onChange={(e) => set("emitter_flow_lph", e.target.value)} /></Field>
      </div>

      <div className="row" style={{ marginTop: 22, alignItems: "center" }}>
        <button className="btn" style={{ padding: "12px 22px", fontSize: 14.5 }}
          onClick={submit} disabled={saving}>
          {saving ? "⏳ " + t("calculating") : "🧮 " + t("calc_schedule")}
        </button>
        {saving && <span style={{ color: "var(--muted)", fontSize: 12.5 }}>{t("provisioning")}</span>}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="field"><label>{label}</label>{children}</div>;
}
