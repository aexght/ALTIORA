/**
 * HeroIllustration — Abstract SVG illustration for the landing page hero.
 *
 * A very subtle abstract composition consisting of soft marble-like 
 * flowing curves, thin elegant contour lines, and subtle geometric arcs.
 * Fits the premium, minimal, editorial ALTIORA aesthetic with no obvious 
 * "AI" symbols or dashboard cards.
 */

export function HeroIllustration({ className = '' }) {
  return (
    <svg
      viewBox="0 0 480 480"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
      role="img"
    >
      <defs>
        <filter id="altiora-blur-lg" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="32" />
        </filter>
        <filter id="altiora-blur-md" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="16" />
        </filter>
      </defs>

      {/* ── Soft Marble/Glow Backdrop ────────────────── */}
      <circle cx="240" cy="240" r="160" fill="#f5f5f4" filter="url(#altiora-blur-lg)" opacity="0.9" />
      <ellipse cx="320" cy="180" rx="140" ry="100" fill="#e7e5e4" filter="url(#altiora-blur-md)" opacity="0.6" />
      <ellipse cx="140" cy="320" rx="100" ry="160" fill="#e7e5e4" filter="url(#altiora-blur-lg)" opacity="0.5" />

      {/* ── Flowing Contour Lines ────────────────────── */}
      <path 
        d="M -40,120 Q 150,-20 320,180 T 520,300" 
        stroke="#d6d3d1" 
        strokeWidth="1" 
        fill="none" 
        opacity="0.6" 
      />
      <path 
        d="M -20,180 Q 180,20 350,220 T 540,360" 
        stroke="#d6d3d1" 
        strokeWidth="1" 
        fill="none" 
        opacity="0.5" 
      />
      <path 
        d="M 0,240 Q 210,60 380,260 T 560,420" 
        stroke="#d6d3d1" 
        strokeWidth="0.5" 
        fill="none" 
        opacity="0.4" 
      />
      <path 
        d="M 40,320 Q 250,140 420,340 T 600,500" 
        stroke="#e7e5e4" 
        strokeWidth="1" 
        fill="none" 
        opacity="0.7" 
      />
      <path 
        d="M 120,400 Q 300,240 460,420" 
        stroke="#e7e5e4" 
        strokeWidth="0.75" 
        fill="none" 
        opacity="0.5" 
      />

      {/* ── Subtle Geometric Arcs & Circles ──────────── */}
      {/* Outer faint ring */}
      <circle cx="240" cy="240" r="180" stroke="#a8a29e" strokeWidth="0.5" strokeDasharray="2 16" fill="none" opacity="0.25" />
      
      {/* Inner offset ring */}
      <circle cx="250" cy="230" r="110" stroke="#a8a29e" strokeWidth="0.5" strokeDasharray="4 8" fill="none" opacity="0.35" />
      
      {/* Focal ring */}
      <circle cx="210" cy="260" r="60" stroke="#d6d3d1" strokeWidth="0.75" fill="none" opacity="0.5" />

      {/* Abstract geometric focal point (triangle) */}
      <path d="M 210,245 L 225,270 L 195,270 Z" stroke="#78716c" strokeWidth="0.75" fill="none" opacity="0.3" />

      {/* ── Delicate Floating Particles ──────────────── */}
      <circle cx="160" cy="180" r="1.5" fill="#78716c" opacity="0.4" />
      <circle cx="340" cy="280" r="2" fill="#78716c" opacity="0.3" />
      <circle cx="300" cy="140" r="1" fill="#a8a29e" opacity="0.5" />
      <circle cx="120" cy="280" r="2.5" fill="#a8a29e" opacity="0.2" />
      <circle cx="380" cy="360" r="1.5" fill="#a8a29e" opacity="0.4" />
      <circle cx="270" cy="340" r="1" fill="#78716c" opacity="0.3" />

    </svg>
  );
}

export default HeroIllustration;
