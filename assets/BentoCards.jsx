import { useState, useRef, useCallback } from "react";
import { motion } from "motion/react";

// ================================================
// Shared styles & utilities
// ================================================

const cardBase = {
  position: "relative",
  overflow: "hidden",
  borderRadius: "1.5rem",
  border: "1px solid rgba(255, 255, 255, 0.03)",
  boxShadow:
    "0 10px 30px -15px rgba(0,0,0,0.6), 0 5px 15px -10px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.03)",
  clipPath: "inset(-10px)",
  transformStyle: "preserve-3d",
  backfaceVisibility: "hidden",
  transition: "all 0s cubic-bezier(0.4, 0, 0.2, 1)",
  cursor: "default",
};

const bgOverlay = {
  position: "absolute",
  inset: 0,
  background: "rgba(22, 22, 28, 0.97)",
  backdropFilter: "blur(18px)",
  WebkitBackdropFilter: "blur(18px)",
  borderRadius: "1.5rem",
  boxShadow: "inset 0 1px 0 rgba(255,255,255,0.02)",
  pointerEvents: "none",
  zIndex: 1,
};

const contentLayer = {
  position: "relative",
  zIndex: 3,
  width: "100%",
  height: "100%",
};

const iconBoxStyle = {
  width: "2.75rem",
  height: "2.75rem",
  borderRadius: "0.875rem",
  background: "rgba(255, 255, 255, 0.05)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  flexShrink: 0,
};

const headingStyle = {
  fontSize: "1.125rem",
  fontWeight: 600,
  color: "white",
  margin: 0,
  lineHeight: 1.3,
  fontFamily: "var(--default-font-family, inherit)",
};

const subtextStyle = {
  fontSize: "0.8rem",
  color: "rgba(255, 255, 255, 0.3)",
  lineHeight: 1.4,
  margin: 0,
  fontFamily: "var(--default-font-family, inherit)",
};

const iconSvgProps = {
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "rgba(255,255,255,0.5)",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

// Cursor-tracking border glow
const CursorBorderGlow = ({ mousePos, isHovered }) => {
  if (!isHovered) return null;
  const { x, y } = mousePos;
  return (
    <motion.div
      style={{
        position: "absolute",
        inset: 0,
        borderRadius: "1.5rem",
        padding: "1px",
        background: `radial-gradient(circle 200px at ${x}px ${y}px, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1) 50%, rgba(255, 255, 255, 0.03) 100%)`,
        WebkitMask:
          "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
        WebkitMaskComposite: "xor",
        maskComposite: "exclude",
        pointerEvents: "none",
        zIndex: 2,
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    />
  );
};

// Tilt + mouse position hook
function useTilt() {
  const cardRef = useRef(null);
  const [tiltStyle, setTiltStyle] = useState({});
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePos({ x, y });
    const rotateX = ((y - rect.height / 2) / (rect.height / 2)) * -3;
    const rotateY = ((x - rect.width / 2) / (rect.width / 2)) * 3;
    setTiltStyle({
      transform: `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
    });
  }, []);

  const resetTilt = useCallback(() => {
    setTiltStyle({
      transform: "perspective(1200px) rotateX(0deg) rotateY(0deg)",
    });
  }, []);

  return { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos };
}

// ================================================
// 1. TRANSPARENCY CARD
// Opaque → semi-transparent on hover, revealing
// stylized "source code" lines underneath.
// ================================================

const codeLines = [
  { w: "60%", c: "rgba(124, 58, 237, 0.3)", indent: 0 },
  { w: "45%", c: "rgba(59, 130, 246, 0.25)", indent: 1 },
  { w: "75%", c: "rgba(255, 255, 255, 0.08)", indent: 1 },
  { w: "30%", c: "rgba(124, 58, 237, 0.2)", indent: 2 },
  { w: "55%", c: "rgba(255, 255, 255, 0.06)", indent: 2 },
  { w: "40%", c: "rgba(59, 130, 246, 0.2)", indent: 1 },
  { w: "65%", c: "rgba(255, 255, 255, 0.07)", indent: 0 },
  { w: "35%", c: "rgba(124, 58, 237, 0.25)", indent: 1 },
];

const TransparencyCard = ({ className = "", style = {} }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos } =
    useTilt();

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{ ...cardBase, ...tiltStyle, ...style }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        resetTilt();
      }}
    >
      {/* Background overlay – partially transparent by default, fades more on hover */}
      <motion.div
        style={bgOverlay}
        animate={{
          opacity: isHovered ? 0.12 : 0.55,
        }}
        transition={{ duration: 0.55, ease: [0.25, 0.4, 0.4, 1] }}
      />

      {/* Source code pattern (visible when transparent) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: "1.25rem",
          zIndex: 0,
          display: "flex",
          flexDirection: "column",
          gap: "0.4rem",
          paddingTop: "5rem",
        }}
      >
        {codeLines.map((line, i) => (
          <div
            key={i}
            style={{
              width: line.w,
              height: "0.3rem",
              borderRadius: "2px",
              background: line.c,
              marginLeft: `${line.indent * 1}rem`,
            }}
          />
        ))}
      </div>

      {/* Grid overlay for extra texture */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "20px 20px",
          zIndex: 0,
          pointerEvents: "none",
        }}
      />

      <CursorBorderGlow mousePos={mousePos} isHovered={isHovered} />

      {/* Content */}
      <div
        style={{
          ...contentLayer,
          padding: "1.25rem",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={iconBoxStyle}>
          <svg {...iconSvgProps}>
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        </div>

        {/* Spacer pushes heading to true bottom */}
        <div style={{ flex: 1 }} />

        {/* Subtext right-aligned, above heading */}
        <motion.p
          style={{
            ...subtextStyle,
            textAlign: "right",
            marginBottom: "0.75rem",
          }}
          animate={{
            opacity: isHovered ? 0.95 : 0.55,
            color: isHovered
              ? "rgba(255, 255, 255, 0.85)"
              : "rgba(255, 255, 255, 0.5)",
          }}
          transition={{ duration: 0.55, ease: [0.25, 0.4, 0.4, 1] }}
        >
          Open-source. All sources publicly verifiable.
        </motion.p>
        <h3 style={{ ...headingStyle }}>Transparency</h3>
      </div>
    </motion.div>
  );
};

// ================================================
// 2. FOCUSED CARD
// Dense wall of financial terms. On hover,
// everything blurs except the key phrase.
// ================================================

const FocusedCard = ({ className = "", style = {} }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos } =
    useTilt();

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{ ...cardBase, ...tiltStyle, ...style }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        resetTilt();
      }}
    >
      <div style={bgOverlay} />
      <CursorBorderGlow mousePos={mousePos} isHovered={isHovered} />

      <div
        style={{
          ...contentLayer,
          padding: "1.5rem",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          overflow: "hidden",
        }}
      >
        <div style={iconBoxStyle}>
          <svg {...iconSvgProps}>
            <circle cx="12" cy="12" r="10" />
            <line x1="22" y1="12" x2="18" y2="12" />
            <line x1="6" y1="12" x2="2" y2="12" />
            <line x1="12" y1="6" x2="12" y2="2" />
            <line x1="12" y1="22" x2="12" y2="18" />
          </svg>
        </div>

        <div>
          {/* Dense inline text with embedded key phrase */}
          <div
            style={{
              fontSize: "0.6rem",
              lineHeight: 1.7,
              position: "relative",
              fontFamily: "var(--default-font-family, inherit)",
              marginBottom: "0.5rem",
            }}
          >
            {/* Noise text – before key phrase */}
            <motion.span
              style={{ color: "rgba(255,255,255,0.25)" }}
              animate={{
                filter: isHovered ? "blur(2.5px)" : "blur(1px)",
                opacity: isHovered ? 0.15 : 0.35,
              }}
              transition={{ duration: 0.45 }}
            >
              Market analysis · Portfolio tracking · Risk assessment · Stock
              screening · Benchmark comparison ·{" "}
            </motion.span>

            {/* KEY PHRASE – visible by default, glows brighter on hover */}
            <motion.span
              style={{
                fontWeight: 500,
                display: "inline",
                position: "relative",
                zIndex: 1,
                whiteSpace: "nowrap",
              }}
              animate={{
                color: isHovered
                  ? "rgba(255, 255, 255, 0.95)"
                  : "rgba(255, 255, 255, 0.65)",
                textShadow: isHovered
                  ? "0 0 20px rgba(255, 255, 255, 0.4), 0 0 40px rgba(255, 255, 255, 0.15)"
                  : "0 0 10px rgba(255, 255, 255, 0.1)",
              }}
              transition={{ duration: 0.35, delay: isHovered ? 0.08 : 0 }}
            >
              One framework, zero clutter
            </motion.span>

            {/* Noise text – after key phrase */}
            <motion.span
              style={{ color: "rgba(255,255,255,0.25)" }}
              animate={{
                filter: isHovered ? "blur(2.5px)" : "blur(1px)",
                opacity: isHovered ? 0.15 : 0.35,
              }}
              transition={{ duration: 0.45 }}
            >
              {" "}
              · Technical indicators · Sector analysis · Dividend yields ·
              Earnings reports · Asset allocation
            </motion.span>
          </div>

          <h3 style={headingStyle}>Focused</h3>
        </div>
      </div>
    </motion.div>
  );
};

// ================================================
// 3. CONCISENESS CARD
// Content scrolls up on hover with a mini
// scrollbar indicator. "All within a single scroll."
// ================================================

const ConcisenessCard = ({ className = "", style = {} }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos } =
    useTilt();

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{ ...cardBase, ...tiltStyle, ...style }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        resetTilt();
      }}
    >
      <div style={bgOverlay} />
      <CursorBorderGlow mousePos={mousePos} isHovered={isHovered} />

      {/* Mini scrollbar track – partially scrolled by default */}
      <div
        style={{
          position: "absolute",
          right: "0.6rem",
          bottom: "1.8rem",
          height: "2.5rem",
          width: "3px",
          background: "rgba(255, 255, 255, 0.04)",
          borderRadius: "1.5px",
          zIndex: 4,
          overflow: "hidden",
        }}
      >
        <motion.div
          style={{
            width: "3px",
            height: "30%",
            background: "rgba(255, 255, 255, 0.15)",
            borderRadius: "1.5px",
          }}
          animate={{
            y: isHovered ? "233%" : "100%",
            background: isHovered
              ? "rgba(124, 58, 237, 0.4)"
              : "rgba(255, 255, 255, 0.2)",
          }}
          transition={{ duration: 0.55, ease: [0.25, 0.4, 0.4, 1] }}
        />
      </div>

      {/* Content – overflows, shifts up on hover */}
      <div
        style={{
          ...contentLayer,
          overflow: "hidden",
          padding: "1.25rem",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Icon stays at top */}
        <div style={iconBoxStyle}>
          <svg {...iconSvgProps}>
            <polyline points="4 14 10 14 10 20" />
            <polyline points="20 10 14 10 14 4" />
            <line x1="14" y1="10" x2="21" y2="3" />
            <line x1="3" y1="21" x2="10" y2="14" />
          </svg>
        </div>

        {/* Flexible spacer */}
        <div style={{ flex: 1 }} />

        {/* Bottom: heading with subtext, scrolls up on hover */}
        <motion.div
          animate={{ y: isHovered ? -8 : 0 }}
          transition={{ duration: 0.55, ease: [0.25, 0.4, 0.4, 1] }}
        >
          <motion.p
            style={{
              ...subtextStyle,
              textAlign: "right",
              marginBottom: "0.75rem",
            }}
            animate={{
              opacity: isHovered ? 0.95 : 0.55,
              color: isHovered
                ? "rgba(255, 255, 255, 0.85)"
                : "rgba(255, 255, 255, 0.5)",
            }}
            transition={{ duration: 0.55, ease: [0.25, 0.4, 0.4, 1] }}
          >
            Everything within a single scroll.
          </motion.p>
          <h3 style={headingStyle}>Conciseness</h3>
        </motion.div>
      </div>
    </motion.div>
  );
};

// ================================================
// 4. RELIABILITY CARD
// Verification items with self-drawing checkmarks.
// Sequential animation on hover.
// ================================================

const verifyItems = [
  { label: "Data", hoverLabel: "VNStock", delay: 0 },
  { label: "Frameworks", delay: 0.18 },
  { label: "Results", delay: 0.36 },
];

const VerifyItem = ({ label, hoverLabel, delay, isHovered }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: "0.6rem",
      height: "1.4rem",
    }}
  >
    {/* Status indicator container */}
    <div
      style={{
        width: "16px",
        height: "16px",
        position: "relative",
        flexShrink: 0,
      }}
    >
      {/* Default circle – hidden by default (checkmarks shown instead) */}
      <motion.div
        style={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          border: "1.5px solid rgba(255, 255, 255, 0.12)",
        }}
        animate={{
          opacity: 0,
          scale: 0.5,
        }}
        transition={{ duration: 0.2 }}
      />

      {/* Checkmark SVG – visible by default, brightens on hover */}
      <motion.svg
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ position: "absolute", inset: 0 }}
      >
        <motion.path
          d="M5 12l5 5L20 7"
          stroke="#4ade80"
          initial={{ pathLength: 1, opacity: 0.5 }}
          animate={{
            pathLength: 1,
            opacity: isHovered ? 1 : 0.5,
          }}
          transition={{
            duration: 0.35,
            delay: isHovered ? delay * 0.5 : 0,
            ease: "easeOut",
          }}
        />
      </motion.svg>
    </div>

    {/* Label – visible by default, brightens on hover */}
    <div style={{ position: "relative", display: "inline-flex" }}>
      <motion.span
        style={{
          fontSize: "0.72rem",
          fontFamily: "var(--default-font-family, inherit)",
        }}
        animate={{
          color: isHovered
            ? "rgba(255, 255, 255, 0.7)"
            : "rgba(255, 255, 255, 0.4)",
          opacity: hoverLabel && isHovered ? 0 : 1,
        }}
        transition={{ duration: 0.3, delay: isHovered ? delay : 0 }}
      >
        {label}
      </motion.span>
      {hoverLabel && (
        <motion.span
          style={{
            fontSize: "0.72rem",
            fontFamily: "var(--default-font-family, inherit)",
            position: "absolute",
            left: 0,
            top: 0,
          }}
          animate={{
            color: isHovered
              ? "rgba(255, 255, 255, 0.7)"
              : "rgba(255, 255, 255, 0.4)",
            opacity: isHovered ? 1 : 0,
          }}
          transition={{ duration: 0.3, delay: isHovered ? delay : 0 }}
        >
          {hoverLabel}
        </motion.span>
      )}
    </div>
  </div>
);

const ReliabilityCard = ({ className = "", style = {} }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos } =
    useTilt();

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{ ...cardBase, ...tiltStyle, ...style }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        resetTilt();
      }}
    >
      <div style={bgOverlay} />
      <CursorBorderGlow mousePos={mousePos} isHovered={isHovered} />

      <div
        style={{
          ...contentLayer,
          padding: "1.25rem",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        {/* Shield icon */}
        <div style={iconBoxStyle}>
          <svg {...iconSvgProps}>
            <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
            <path d="m9 12 2 2 4-4" />
          </svg>
        </div>

        {/* Verification items */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.45rem",
            marginTop: "0.5rem",
          }}
        >
          {verifyItems.map((item) => (
            <VerifyItem
              key={item.label}
              label={item.label}
              hoverLabel={item.hoverLabel}
              delay={item.delay}
              isHovered={isHovered}
            />
          ))}
        </div>

        {/* Heading */}
        <div style={{ marginTop: "auto", paddingTop: "0.5rem" }}>
          <h3 style={headingStyle}>Reliability</h3>
        </div>
      </div>
    </motion.div>
  );
};

// ================================================
// 5. INSTRUCTIVENESS CARD
// Floating concept badges appear on hover with
// staggered animation. Knowledge radiating out.
// ================================================

const concepts = [
  { text: "P/E", top: "18%", left: "28%", delay: 0 },
  { text: "DCF", top: "12%", left: "52%", delay: 0.06 },
  { text: "ROI", top: "22%", left: "72%", delay: 0.1 },
  { text: "EPS", top: "35%", left: "20%", delay: 0.14 },
  { text: "WACC", top: "30%", left: "44%", delay: 0.18 },
  { text: "CAGR", top: "38%", left: "65%", delay: 0.22 },
  { text: "Beta", top: "15%", left: "38%", delay: 0.08 },
  { text: "Alpha", top: "32%", left: "82%", delay: 0.26 },
];

const ConceptBadge = ({ text, top, left, delay, isHovered }) => (
  <motion.div
    style={{
      position: "absolute",
      top,
      left,
      background: isHovered
        ? "rgba(124, 58, 237, 0.15)"
        : "rgba(124, 58, 237, 0.06)",
      border: `1px solid ${isHovered ? "rgba(124, 58, 237, 0.25)" : "rgba(124, 58, 237, 0.1)"}`,
      borderRadius: "0.5rem",
      padding: "0.2rem 0.65rem",
      fontSize: "0.68rem",
      fontWeight: 500,
      fontFamily: "var(--default-font-family, inherit)",
      color: "rgba(255, 255, 255, 0.65)",
      whiteSpace: "nowrap",
      pointerEvents: "none",
    }}
    animate={{
      opacity: isHovered ? 1 : 0.5,
      y: 0,
      scale: isHovered ? 1.05 : 1,
    }}
    transition={{
      duration: 0.35,
      delay: isHovered ? delay * 0.5 : 0,
      ease: "easeOut",
    }}
  >
    {text}
  </motion.div>
);

const InstructivenessCard = ({ className = "", style = {} }) => {
  const [isHovered, setIsHovered] = useState(false);
  const { cardRef, tiltStyle, handleMouseMove, resetTilt, mousePos } =
    useTilt();

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{ ...cardBase, ...tiltStyle, ...style }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        resetTilt();
      }}
    >
      <div style={bgOverlay} />
      <CursorBorderGlow mousePos={mousePos} isHovered={isHovered} />

      {/* Floating concept badges */}
      {concepts.map((c) => (
        <ConceptBadge
          key={c.text}
          text={c.text}
          top={c.top}
          left={c.left}
          delay={c.delay}
          isHovered={isHovered}
        />
      ))}

      {/* Subtle radial glow behind icon on hover */}
      <motion.div
        style={{
          position: "absolute",
          top: "0.5rem",
          left: "0.5rem",
          width: "8rem",
          height: "8rem",
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(124, 58, 237, 0.12) 0%, transparent 70%)",
          pointerEvents: "none",
          zIndex: 0,
        }}
        animate={{ opacity: isHovered ? 1 : 0.4, scale: isHovered ? 1.2 : 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      />

      <div
        style={{
          ...contentLayer,
          padding: "2rem",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        {/* Graduation cap icon */}
        <div style={iconBoxStyle}>
          <svg {...iconSvgProps}>
            <path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z" />
            <path d="M22 10v6" />
            <path d="M6 12.5V16c0 1 2 3 6 3s6-2 6-3v-3.5" />
          </svg>
        </div>

        <div>
          <motion.p
            style={{ ...subtextStyle, marginBottom: "0.25rem" }}
            animate={{
              color: isHovered
                ? "rgba(255, 255, 255, 0.65)"
                : "rgba(255, 255, 255, 0.4)",
            }}
            transition={{ duration: 0.4, delay: isHovered ? 0.15 : 0 }}
          >
            Built to educate, not to sell. By helping investors with their
            investment portfolios, we're also building our own professional
            portfolio.
          </motion.p>
          <h3 style={headingStyle}>Instructiveness</h3>
        </div>
      </div>
    </motion.div>
  );
};

// ================================================
// Exports
// ================================================

export {
  TransparencyCard,
  FocusedCard,
  ConcisenessCard,
  ReliabilityCard,
  InstructivenessCard,
};
