import { useLang } from "../i18n";
import { LogoMark } from "../components/Logo";

const FEATURES: { icon: string; key: string }[] = [
  { icon: "🌡️", key: "f_eto" },
  { icon: "🛰️", key: "f_sources" },
  { icon: "🌱", key: "f_crops" },
  { icon: "💧", key: "f_schedule" },
  { icon: "📊", key: "f_validate" },
  { icon: "📄", key: "f_reports" },
];

export function Landing({ onSignIn, onGuest }: { onSignIn: () => void; onGuest: () => void }) {
  const { t, lang, toggle } = useLang();
  return (
    <div className="landing">
      <div className="landing-topbar">
        <div className="row" style={{ gap: 10, alignItems: "center" }}>
          <LogoMark size={34} />
          <b style={{ fontSize: 15 }}>
            <span style={{ color: "#2E7D32" }}>Smart</span><span style={{ color: "#0288D1" }}>Ponics</span>
          </b>
        </div>
        <div className="row" style={{ gap: 8 }}>
          <button className="btn ghost" onClick={toggle}>{lang === "en" ? "العربية" : "English"}</button>
          <button className="btn secondary" onClick={onSignIn}>{t("login")}</button>
        </div>
      </div>

      <section className="hero">
        <LogoMark size={96} />
        <h1 className="hero-title">{t("app_title")}</h1>
        <p className="hero-sub">{t("landing_tagline")}</p>
        <div className="row" style={{ justifyContent: "center", gap: 12, marginTop: 22 }}>
          <button className="btn" style={{ padding: "13px 26px", fontSize: 15 }} onClick={onSignIn}>
            🔐 {t("login")}
          </button>
          <button className="btn secondary" style={{ padding: "13px 26px", fontSize: 15 }} onClick={onGuest}>
            👤 {t("guest_enter")}
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
        <LogoMark size={26} />
        <span>SmartPonics Global Consult · {t("app_title")}</span>
      </footer>
    </div>
  );
}
