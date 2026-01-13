import { useState, useRef } from "react";
import { motion } from "motion/react";

const MagicBentoCard = ({
  children,
  className = "",
  spotlightRadius = 60,
  enableTilt = true,
  enableMagnetism = true,
  style = {},
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const [tiltStyle, setTiltStyle] = useState({});
  const cardRef = useRef(null);

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setMousePosition({ x, y });

    if (enableTilt) {
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -8;
      const rotateY = ((x - centerX) / centerX) * 8;

      setTiltStyle({
        transform: `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.01, 1.01, 1.01)`,
      });
    }
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setTiltStyle({
      transform:
        "perspective(1200px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)",
    });
  };

  return (
    <motion.div
      ref={cardRef}
      className={className}
      style={{
        position: "relative",
        overflow: "hidden",
        borderRadius: "2rem",
        background: "rgba(255, 255, 255, 0.02)",
        border: "1px solid rgba(255, 255, 255, 0.06)",
        backdropFilter: "blur(24px)",
        transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        ...tiltStyle,
        ...style,
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      whileHover={enableMagnetism ? { scale: 1.02 } : {}}
    >
      {/* Spotlight effect */}
      {isHovered && (
        <motion.div
          style={{
            position: "absolute",
            width: `${spotlightRadius * 2}px`,
            height: `${spotlightRadius * 2}px`,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(124, 58, 237, 0.4) 0%, rgba(124, 58, 237, 0.2) 30%, transparent 70%)",
            pointerEvents: "none",
            left: `${mousePosition.x - spotlightRadius}px`,
            top: `${mousePosition.y - spotlightRadius}px`,
            zIndex: 1,
            filter: "blur(20px)",
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        />
      )}

      {/* Enhanced glow border effect on hover */}
      {isHovered && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            borderRadius: "2rem",
            padding: "1px",
            background:
              "linear-gradient(135deg, rgba(124, 58, 237, 0.6) 0%, rgba(59, 130, 246, 0.3) 50%, rgba(124, 58, 237, 0.6) 100%)",
            WebkitMask:
              "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
            WebkitMaskComposite: "xor",
            maskComposite: "exclude",
            pointerEvents: "none",
            zIndex: 2,
            animation: "borderRotate 3s linear infinite",
          }}
        />
      )}

      {/* Secondary subtle glow */}
      {isHovered && (
        <div
          style={{
            position: "absolute",
            inset: "-2px",
            borderRadius: "2rem",
            background:
              "radial-gradient(800px circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(124, 58, 237, 0.15), transparent 40%)",
            pointerEvents: "none",
            zIndex: 0,
            opacity: 0.6,
          }}
        />
      )}

      {/* Content */}
      <div
        style={{
          position: "relative",
          zIndex: 3,
          width: "100%",
          height: "100%",
        }}
      >
        {children}
      </div>

      <style>
        {`
          @keyframes borderRotate {
            0% {
              filter: hue-rotate(0deg);
            }
            100% {
              filter: hue-rotate(360deg);
            }
          }
        `}
      </style>
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
