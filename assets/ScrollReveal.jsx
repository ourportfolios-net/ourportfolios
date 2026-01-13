import React, { useRef, useEffect, useState } from "react";
import { motion } from "motion/react";

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

  return (
    <div ref={ref} className={className} style={{ width: "100%", ...style }}>
      <motion.div
        style={{ width: "100%" }}
        initial={{
          opacity: initialOpacity,
          filter: `blur(${blurAmount}px)`,
          scale: initialScale,
        }}
        animate={
          isInView ? { opacity: 1, filter: "blur(0px)", scale: 1 } : undefined
        }
        transition={{ duration, delay, ease: [0.25, 0.4, 0.4, 1] }}
      >
        {children}
      </motion.div>
    </div>
  );
};

export { ScrollReveal };
export default ScrollReveal;
