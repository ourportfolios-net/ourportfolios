import { useId } from "react";

const ShinyText = ({
  text,
  disabled = false,
  speed = 2,
  className = "",
  color = "#b5b5b5",
  shineColor = "#ffffff",
  spread = 120,
  yoyo = false,
  pauseOnHover = false,
  direction = "left",
  delay = 0,
  style = {},
}) => {
  const id = useId().replace(/:/g, "");
  const animName = `shiny-${id}`;
  const from = direction === "left" ? "150% center" : "-50% center";
  const to = direction === "left" ? "-50% center" : "150% center";

  const keyframes = yoyo
    ? `@keyframes ${animName}{0%{background-position:${from}}50%{background-position:${to}}100%{background-position:${from}}}`
    : `@keyframes ${animName}{from{background-position:${from}}to{background-position:${to}}}`;

  const totalDuration = yoyo ? speed * 2 : speed;

  return (
    <>
      <style>{keyframes}</style>
      <span
        className={className}
        style={{
          display: "inline-block",
          backgroundImage: `linear-gradient(${spread}deg, ${color} 0%, ${color} 35%, ${shineColor} 50%, ${color} 65%, ${color} 100%)`,
          backgroundSize: "200% auto",
          WebkitBackgroundClip: "text",
          backgroundClip: "text",
          WebkitTextFillColor: "transparent",
          animation: disabled
            ? "none"
            : `${animName} ${totalDuration}s linear ${delay}s infinite`,
          ...style,
        }}
        onMouseEnter={
          pauseOnHover
            ? (e) => (e.currentTarget.style.animationPlayState = "paused")
            : undefined
        }
        onMouseLeave={
          pauseOnHover
            ? (e) => (e.currentTarget.style.animationPlayState = "running")
            : undefined
        }
      >
        {text}
      </span>
    </>
  );
};

export default ShinyText;
