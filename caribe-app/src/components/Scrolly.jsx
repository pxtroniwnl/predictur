import { useEffect, useRef, useState, Children, cloneElement, isValidElement } from "react";

/**
 * Layout sticky-scrolly:
 *  - Columna izquierda (graphic) sticky
 *  - Columna derecha con steps que disparan el cambio de "activeIndex"
 *
 * Uso:
 *   <Scrolly graphic={(activeIndex) => <Chart scene={scenes[activeIndex]} />}>
 *     <Step>Texto del step 0...</Step>
 *     <Step>Texto del step 1...</Step>
 *   </Scrolly>
 */
export default function Scrolly({ graphic, children, offsetTop = "10vh" }) {
  const [active, setActive] = useState(0);
  const stepsRef = useRef([]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        // Tomar el step más visible cerca del centro
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) {
          const idx = stepsRef.current.indexOf(visible[0].target);
          if (idx !== -1) setActive(idx);
        }
      },
      {
        // Trigger zone: una franja en el medio-superior del viewport
        rootMargin: "-40% 0px -45% 0px",
        threshold: [0, 0.25, 0.5, 0.75, 1],
      }
    );

    stepsRef.current.forEach((el) => el && observer.observe(el));
    return () => observer.disconnect();
  }, [children]);

  const steps = Children.toArray(children);

  return (
    <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
      {/* Sticky graphic column */}
      <div className="lg:col-span-7 lg:sticky lg:self-start" style={{ top: offsetTop, height: "fit-content" }}>
        <div className="aspect-[4/3] lg:aspect-auto lg:h-[78vh] flex items-center justify-center">
          {graphic(active)}
        </div>
      </div>

      {/* Steps column */}
      <div className="lg:col-span-5 flex flex-col gap-[60vh] py-[20vh]">
        {steps.map((child, i) => (
          <div
            key={i}
            ref={(el) => (stepsRef.current[i] = el)}
            data-active={active === i}
            className="transition-opacity duration-500"
            style={{ opacity: active === i ? 1 : 0.35 }}
          >
            {isValidElement(child) ? cloneElement(child, { active: active === i, index: i }) : child}
          </div>
        ))}
      </div>
    </div>
  );
}

export function Step({ children, active }) {
  return (
    <div
      className={`max-w-prose transition-transform duration-500 ${
        active ? "translate-y-0" : "translate-y-1"
      }`}
    >
      {children}
    </div>
  );
}
