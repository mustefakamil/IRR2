// Thin fetch wrapper for the FAO-56 backend API.
const BASE = "";

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
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
  crops: (category?: string) =>
    req<Crop[]>(`/api/catalog/crops${category ? `?category=${encodeURIComponent(category)}` : ""}`),
  categories: () => req<string[]>("/api/catalog/categories"),
  soils: () => req<Soil[]>("/api/catalog/soils"),
  systems: () => req<System[]>("/api/catalog/systems"),
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
  dashboard: (id: number) => req<any>(`/api/projects/${id}/dashboard`),
  schedule: (id: number) =>
    req<{ daily: DailyRow[]; summary: Summary }>(`/api/projects/${id}/schedule`),
  calendar: (id: number) => req<{ events: any[] }>(`/api/projects/${id}/calendar`),
  etoDetail: (id: number, date: string) =>
    req<any>(`/api/projects/${id}/eto-detail?the_date=${date}`),
  reportExcelUrl: (id: number) => `/api/projects/${id}/report/excel`,
  reportCsvUrl: (id: number) => `/api/projects/${id}/report/csv`,
};
