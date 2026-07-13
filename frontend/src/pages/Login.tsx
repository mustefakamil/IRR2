import { useState } from "react";
import { api, auth } from "../api";
import { useLang } from "../i18n";
import { LogoMark } from "../components/Logo";

export function Login({ onSuccess, onBack, onGuest }:
  { onSuccess: () => void; onBack?: () => void; onGuest?: () => void }) {
  const { t, lang, toggle } = useLang();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(null); setBusy(true);
    try {
      const r = await api.login(username.trim(), password);
      auth.token = r.token;
      onSuccess();
    } catch {
      setErr(t("login_error"));
    } finally { setBusy(false); }
  };

  return (
    <div className="login-wrap">
      <form className="login-card" onSubmit={submit}>
        <div className="login-brand">
          <LogoMark size={62} />
          <h1><span style={{ color: "#2E7D32" }}>Smart</span><span style={{ color: "#0288D1" }}>Ponics</span></h1>
          <p>{t("app_sub")}</p>
        </div>
        {err && <div className="err" style={{ marginBottom: 12 }}>{err}</div>}
        <div className="field" style={{ marginBottom: 12 }}>
          <label>{t("username")}</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)}
            autoFocus autoComplete="username" />
        </div>
        <div className="field" style={{ marginBottom: 18 }}>
          <label>{t("password")}</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password" />
        </div>
        <button className="btn" type="submit" disabled={busy}
          style={{ width: "100%", justifyContent: "center" }}>
          {busy ? "…" : "🔐 " + t("login")}
        </button>
        {onGuest && (
          <button type="button" className="btn secondary" onClick={onGuest}
            style={{ width: "100%", justifyContent: "center", marginTop: 10 }}>
            👤 {t("guest_login")}
          </button>
        )}
        <div className="row" style={{ justifyContent: "space-between", marginTop: 12 }}>
          {onBack && <button type="button" className="btn ghost" onClick={onBack}>← {t("app_title")}</button>}
          <button type="button" className="btn ghost" onClick={toggle}>
            {lang === "en" ? "🇸🇦 العربية" : "🇬🇧 English"}
          </button>
        </div>
        <p className="login-hint">admin / admin123 · guest / guest</p>
      </form>
    </div>
  );
}
