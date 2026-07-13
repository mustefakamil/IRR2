// SmartPonics Global Consult logo. Uses the embedded high-res PNG when provided
// (see logoData.ts); otherwise falls back to a self-contained SVG rendition.
import { LOGO_PNG } from "./logoData";

export function LogoMark({ size = 48 }: { size?: number }) {
  if (LOGO_PNG) {
    return <img src={LOGO_PNG} alt="SmartPonics"
      style={{ height: size * 1.15, width: "auto", objectFit: "contain" }} />;
  }
  return (
    <svg width={size} height={size * 1.15} viewBox="0 0 120 138" fill="none"
      xmlns="http://www.w3.org/2000/svg" role="img" aria-label="SmartPonics">
      <defs>
        <linearGradient id="sp-green" x1="20" y1="10" x2="95" y2="80" gradientUnits="userSpaceOnUse">
          <stop stopColor="#8BC34A" />
          <stop offset="1" stopColor="#26A69A" />
        </linearGradient>
        <linearGradient id="sp-blue" x1="30" y1="60" x2="100" y2="130" gradientUnits="userSpaceOnUse">
          <stop stopColor="#4FC3F7" />
          <stop offset="1" stopColor="#0277BD" />
        </linearGradient>
        <linearGradient id="sp-leaf" x1="78" y1="30" x2="110" y2="70" gradientUnits="userSpaceOnUse">
          <stop stopColor="#9CCC65" />
          <stop offset="1" stopColor="#2E7D32" />
        </linearGradient>
      </defs>
      {/* upper green ribbon */}
      <path d="M33 20 C 60 14, 92 30, 70 62 C 58 79, 40 74, 52 60 C 62 48, 46 44, 40 55"
        stroke="url(#sp-green)" strokeWidth="15" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {/* lower blue ribbon (mirror swoop) */}
      <path d="M70 62 C 48 74, 30 92, 52 106 C 66 116, 92 108, 78 90 C 70 79, 84 74, 90 84"
        stroke="url(#sp-blue)" strokeWidth="15" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      {/* leaf */}
      <path d="M84 34 C 104 30, 112 44, 98 58 C 90 66, 78 62, 80 50 C 81 44, 86 42, 90 44"
        fill="url(#sp-leaf)" />
      <path d="M88 40 C 92 47, 93 52, 92 58" stroke="#ffffff" strokeWidth="1.6"
        strokeLinecap="round" opacity="0.7" fill="none" />
    </svg>
  );
}

export function LogoFull({ size = 64, stacked = true }: { size?: number; stacked?: boolean }) {
  // The PNG lockup already includes the wordmark, so show it alone.
  if (LOGO_PNG) {
    return <img src={LOGO_PNG} alt="SmartPonics Global Consult"
      style={{ height: size * 2.1, width: "auto", maxWidth: "100%", objectFit: "contain" }} />;
  }
  return (
    <div style={{ display: "flex", flexDirection: stacked ? "column" : "row",
      alignItems: "center", gap: stacked ? 6 : 12 }}>
      <LogoMark size={size} />
      <div style={{ textAlign: "center", lineHeight: 1.05 }}>
        <div style={{ fontWeight: 800, fontSize: size * 0.42, letterSpacing: "-0.5px" }}>
          <span style={{ color: "#2E7D32" }}>Smart</span>
          <span style={{ color: "#0288D1" }}>Ponics</span>
        </div>
        <div style={{ fontWeight: 700, fontSize: size * 0.24, color: "#1a2027",
          letterSpacing: "2px", textTransform: "uppercase" }}>
          Global Consult
        </div>
      </div>
    </div>
  );
}
