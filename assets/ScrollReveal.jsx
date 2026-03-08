import { useRef, useEffect, useState } from "react";

const ScrollReveal = ({
  children,
  className = "",
  style = {},
  blurAmount = 10,
  initialOpacity = 0.4,
  initialScale = 0.98,
  duration = 0.4,
  delay = 0,
  threshold = 0.1,
  triggerOnce = true,
}) => {
  const ref = useRef(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          if (triggerOnce) observer.disconnect();
        }
      },
      { threshold, rootMargin: "0px 0px -20px 0px" }
    );

    observer.observe(element);
    return () => observer.disconnect();
  }, [threshold, triggerOnce]);

  const ease = "cubic-bezier(0.25, 0.4, 0.4, 1)";
  const t = `opacity ${duration}s ${ease} ${delay}s, filter ${duration}s ${ease} ${delay}s, transform ${duration}s ${ease} ${delay}s`;

  return (
    <div ref={ref} className={className} style={{ width: "100%", ...style }}>
      <div
        style={{
          width: "100%",
          opacity: isInView ? 1 : initialOpacity,
          filter: isInView ? "blur(0px)" : `blur(${blurAmount}px)`,
          transform: isInView ? "scale(1)" : `scale(${initialScale})`,
          transition: t,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export { ScrollReveal };
export default ScrollReveal;
