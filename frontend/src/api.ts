// Thin fetch wrapper for the FAO-56 backend API.
const BASE = "";

export const auth = {
  get token() { return localStorage.getItem("token"); },
  set token(v: string | null) {
    if (v) localStorage.setItem("token", v);
    else localStorage.removeItem("token");
  },
  logout() { localStorage.removeItem("token"); location.reload(); },
};

function authHeaders(): Record<string, string> {
  const t = auth.token;
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json", ...authHeaders() },
    ...opts,
  });
  if (res.status === 401) {
    auth.token = null;
    if (!path.endsWith("/login")) location.reload();
    throw new Error("Not authenticated");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Authenticated file download (reports can't use plain <a href> because the
// bearer token must be attached).
async function downloadFile(path: string, fallbackName: string): Promise<void> {
  const res = await fetch(BASE + path, { headers: authHeaders() });
  if (!res.ok) throw new Error(`Download failed (${res.status})`);
  const blob = await res.blob();
  const cd = res.headers.get("Content-Disposition") || "";
  const m = cd.match(/filename="?([^"]+)"?/);
  const name = m ? m[1] : fallbackName;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

export interface Crop {
  id: number; name_en: string; name_ar: string; scientific_name: string;
  category: string; l_ini: number; l_dev: number; l_mid: number; l_late: number;
  kc_ini: number; kc_mid: number; kc_end: number; zr_min: number; zr_max: number;
  p: number; height: number; ky: number; source: string;
}
export interface Soil {
  id: number; name_en: string; name_ar: string; theta_fc: number;
  theta_wp: number; bulk_density: number; infiltration_mm_hr: number;
}
export interface System {
  id: number; name_en: string; name_ar: string; default_efficiency_pct: number;
}
export interface City {
  id: number; name_en: string; name_ar: string; country: string;
  region: string; latitude: number; longitude: number; elevation: number;
}
export interface Project {
  id: number; project_name: string; farm_name: string; field_name: string;
  country: string; region: string; city: string; latitude: number;
  longitude: number; elevation: number; wind_height: number; area_value: number;
  area_unit: string; planting_date: string; crop_id: number; soil_id: number;
  system_id: number; efficiency_pct: number; ecw: number; ece: number;
  strategy_mode: string; deficit_fraction: number; rainfall_method: string;
  n_emitters: number; emitter_flow_lph: number;
  crop: Crop; soil: Soil; system: System;
}
export interface DailyRow {
  day: number; the_date: string; julian_day: number; stage: string;
  eto: number; kc: number; etc: number; rainfall: number; pe: number;
  lr: number; iwr: number; root_depth: number; taw: number; raw: number;
  p: number; ds_begin: number; daily_water_use: number; ds_end: number;
  irrigate: boolean; dn: number; dg: number; volume_m3: number;
  runtime_hours: number | null; deep_percolation: number;
}
export interface Summary {
  days: number; n_irrigations: number; total_etc: number; total_eto: number;
  total_effective_rain: number; total_net_depth: number; total_gross_depth: number;
  total_net_volume_m3: number; total_gross_volume_m3: number; total_runtime_hours: number;
}

export const api = {
  login: (username: string, password: string) =>
    req<{ token: string; username: string; full_name: string }>(
      "/api/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  me: () => req<{ username: string; full_name: string }>("/api/auth/me"),
  changePassword: (current_password: string, new_password: string) =>
    req<any>("/api/auth/change-password",
      { method: "POST", body: JSON.stringify({ current_password, new_password }) }),

  crops: (category?: string) =>
    req<Crop[]>(`/api/catalog/crops${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  categories: () => req<string[]>("/api/catalog/categories"),
  soils: () => req<Soil[]>("/api/catalog/soils"),
  systems: () => req<System[]>("/api/catalog/systems"),
  cities: (region?: string) =>
    req<City[]>(`/api/catalog/cities${region ? `?region=${encodeURIComponent(region)}` : ""}`),
  regions: () => req<string[]>("/api/catalog/regions"),
  projects: () => req<Project[]>("/api/projects"),
  project: (id: number) => req<Project>(`/api/projects/${id}`),
  createProject: (body: any) =>
    req<Project>("/api/projects", { method: "POST", body: JSON.stringify(body) }),
  updateProject: (id: number, body: any) =>
    req<Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  deleteProject: (id: number) =>
    req<void>(`/api/projects/${id}`, { method: "DELETE" }),
  loadSample: () => req<Project>("/api/projects/load-sample", { method: "POST" }),
  climate: (id: number) => req<any[]>(`/api/projects/${id}/climate`),
  clearClimate: (id: number) =>
    req<void>(`/api/projects/${id}/climate`, { method: "DELETE" }),
  bulkClimate: (id: number, days: any[], replace = true) =>
    req<any>(`/api/projects/${id}/climate/bulk`, {
      method: "POST", body: JSON.stringify({ days, replace }),
    }),
  uploadClimate: async (id: number, file: File, replace = true) => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch(`/api/projects/${id}/climate/upload?replace=${replace}`, {
      method: "POST", body: fd,
    });
    if (!res.ok) throw new Error((await res.json()).detail ?? res.statusText);
    return res.json();
  },
  fetchWeather: (id: number, source: string, start?: string, end?: string) => {
    const q = new URLSearchParams({ source });
    if (start) q.set("start", start);
    if (end) q.set("end", end);
    return req<{ inserted: number; source: string; start: string; end: string }>(
      `/api/projects/${id}/climate/fetch?${q.toString()}`, { method: "POST" });
  },
  climateSources: (id: number) =>
    req<{ providers: any[]; available_drivers: number; merge_possible: boolean }>(
      `/api/projects/${id}/climate/sources`),
  fetchMerged: (id: number, start?: string, end?: string, sources?: string[]) => {
    const q = new URLSearchParams();
    if (start) q.set("start", start);
    if (end) q.set("end", end);
    if (sources && sources.length) q.set("sources", sources.join(","));
    return req<{ inserted: number; start: string; end: string; merged_source: string; report: any }>(
      `/api/projects/${id}/climate/fetch-merged?${q.toString()}`, { method: "POST" });
  },
  validate: (id: number, level: string = "L2") =>
    req<any>(`/api/projects/${id}/validate?level=${level}`),
  dashboard: (id: number) => req<any>(`/api/projects/${id}/dashboard`),
  schedule: (id: number) =>
    req<{ daily: DailyRow[]; summary: Summary }>(`/api/projects/${id}/schedule`),
  calendar: (id: number) => req<{ events: any[] }>(`/api/projects/${id}/calendar`),
  etoDetail: (id: number, date: string) =>
    req<any>(`/api/projects/${id}/eto-detail?the_date=${date}`),
  downloadExcel: (id: number) => downloadFile(`/api/projects/${id}/report/excel`, "report.xlsx"),
  downloadCsv: (id: number) => downloadFile(`/api/projects/${id}/report/csv`, "schedule.csv"),
  downloadPdf: (id: number) => downloadFile(`/api/projects/${id}/report/pdf`, "report.pdf"),
};
