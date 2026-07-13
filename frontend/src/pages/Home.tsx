import { useLang } from "../i18n";
import { LogoFull } from "../components/Logo";

const FEATURES: { icon: string; key: string }[] = [
  { icon: "🌡️", key: "f_eto" },
  { icon: "🛰️", key: "f_sources" },
  { icon: "🌱", key: "f_crops" },
  { icon: "💧", key: "f_schedule" },
  { icon: "📊", key: "f_validate" },
  { icon: "📄", key: "f_reports" },
];

export function Home({ onDashboard, onNew }: { onDashboard: () => void; onNew: () => void }) {
  const { t } = useLang();
  return (
    <div>
      <section className="hero" style={{ paddingTop: 14 }}>
        <LogoFull size={88} />
        <p className="hero-sub" style={{ marginTop: 18 }}>{t("landing_tagline")}</p>
        <div className="row" style={{ justifyContent: "center", gap: 12, marginTop: 22 }}>
          <button className="btn" style={{ padding: "13px 26px", fontSize: 15 }} onClick={onDashboard}>
            📊 {t("open_dashboard")}
          </button>
          <button className="btn secondary" style={{ padding: "13px 26px", fontSize: 15 }} onClick={onNew}>
            ➕ {t("new_project")}
          </button>
        </div>
        <p className="hero-method">{t("app_sub")}</p>
      </section>

      <section className="landing-features">
        {FEATURES.map((f) => (
          <div key={f.key} className="feature-card">
            <div className="feature-ic">{f.icon}</div>
            <h4>{t(f.key + "_t")}</h4>
            <p>{t(f.key + "_d")}</p>
          </div>
        ))}
      </section>

      <section className="landing-strip">
        <div><b>81</b><span>{t("s_crops")}</span></div>
        <div><b>95</b><span>{t("s_cities")}</span></div>
        <div><b>5</b><span>{t("s_apis")}</span></div>
        <div><b>FAO-56</b><span>{t("s_method")}</span></div>
      </section>

      <footer className="landing-foot">
        SmartPonics Global Consult · {t("app_title")}
      </footer>
    </div>
  );
}
