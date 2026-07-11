import { useEffect, useState } from "react";
import { api, Crop } from "../api";
import { useLang } from "../i18n";

export function Crops() {
  const { t, lang } = useLang();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [cats, setCats] = useState<string[]>([]);
  const [cat, setCat] = useState<string>("");
  const [q, setQ] = useState("");

  useEffect(() => { api.categories().then(setCats); }, []);
  useEffect(() => { api.crops(cat || undefined).then(setCrops); }, [cat]);

  const filtered = crops.filter((c) =>
    !q || c.name_en.toLowerCase().includes(q.toLowerCase()) || (c.name_ar || "").includes(q));

  return (
    <>
      <div className="row" style={{ marginBottom: 14 }}>
        <select value={cat} onChange={(e) => setCat(e.target.value)}
          style={{ padding: "9px 11px", borderRadius: 8, border: "1px solid var(--line)" }}>
          <option value="">All categories</option>
          {cats.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <input placeholder="Search crop…" value={q} onChange={(e) => setQ(e.target.value)}
          style={{ padding: "9px 11px", borderRadius: 8, border: "1px solid var(--line)", flex: 1, minWidth: 180 }} />
        <span style={{ color: "var(--muted)", fontSize: 13 }}>{filtered.length} crops</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr>
            <th>Crop</th><th>العربية</th><th>Category</th>
            <th>Lini</th><th>Ldev</th><th>Lmid</th><th>Llate</th>
            <th>Kc ini</th><th>Kc mid</th><th>Kc end</th><th>Zr min</th><th>Zr max</th><th>p</th><th>Ky</th><th>Source</th>
          </tr></thead>
          <tbody>
            {filtered.map((c) => (
              <tr key={c.id}>
                <td style={{ textAlign: "start", fontWeight: 600 }}>{c.name_en}</td>
                <td>{c.name_ar}</td><td>{c.category}</td>
                <td>{c.l_ini}</td><td>{c.l_dev}</td><td>{c.l_mid}</td><td>{c.l_late}</td>
                <td>{c.kc_ini}</td><td>{c.kc_mid}</td><td>{c.kc_end}</td>
                <td>{c.zr_min}</td><td>{c.zr_max}</td><td>{c.p}</td><td>{c.ky}</td>
                <td><span className={"pill " + c.source}>{c.source}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
