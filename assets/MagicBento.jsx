import { useState, useRef } from "react";
import { motion } from "motion/react";

const MagicBentoCard = ({
  children,
  className = "",
  enableTilt = false,
  style = {},
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [tiltStyle, setTiltStyle] = useState({});
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    if (!cardRef.current || !enableTilt) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -3;
    const rotateY = ((x - centerX) / centerX) * 3;

    setTiltStyle({
      transform: `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`,
    });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTiltStyle({
      transform: "perspective(1200px) rotateX(0deg) rotateY(0deg)",
    });
  };

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{
        position: "relative",
        overflow: "hidden",
        borderRadius: "1.5rem",
        border: "1px solid rgba(255, 255, 255, 0.03)",
        boxShadow:
          "0 10px 30px -15px rgba(0,0,0,0.6), 0 5px 15px -10px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.03)",
        clipPath: "inset(-10px)",
        transition: "all 0s cubic-bezier(0.4, 0, 0.2, 1)",
        transformStyle: "preserve-3d",
        backfaceVisibility: "hidden",
        ...tiltStyle,
        ...style,
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      whileHover={{ y: -4 }}
    >
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          background: "rgba(22,22,28,0.8)",
          backdropFilter: "blur(18px)",
          WebkitBackdropFilter: "blur(18px)",
          borderRadius: "1.5rem",
          boxShadow: "inset 0 1px 0 rgba(255,255,255,0.02)",
          pointerEvents: "none",
          zIndex: 1,
        }}
      />

      {isHovered && (
        <motion.div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: "1.5rem",
            padding: "1px",
            background: "rgba(124, 58, 237, 0.2)",
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
          transition={{ duration: 0.3 }}
        />
      )}

      <div
        style={{
          position: "relative",
          zIndex: 3,
          width: "100%",
          height: "100%",
          opacity: 0.95,
        }}
      >
        {children}
      </div>
    </motion.div>
  );
};

const MagicBento = ({
  children,
  columns = 3,
  gap = "1rem",
  className = "",
  style = {},
}) => {
  return (
    <div
      className={className}
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: gap,
        width: "100%",
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export { MagicBento, MagicBentoCard };
export default MagicBento;
