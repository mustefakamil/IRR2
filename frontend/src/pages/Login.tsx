import { useState } from "react";
import { api, auth } from "../api";
import { useLang } from "../i18n";

export function Login({ onSuccess }: { onSuccess: () => void }) {
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
          <span className="logo">🌾</span>
          <h1>{t("app_title")}</h1>
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
        <button type="button" className="btn ghost" onClick={toggle}
          style={{ width: "100%", justifyContent: "center", marginTop: 10 }}>
          {lang === "en" ? "🇸🇦 العربية" : "🇬🇧 English"}
        </button>
        <p className="login-hint">Default: admin / admin123</p>
      </form>
    </div>
  );
}
