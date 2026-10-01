import { useEffect, useRef } from "react";
import Section, { Reveal } from "./Section.jsx";

const HIGHLIGHTS = [
  ["01", "Industrial facility", "One-line, cable tray, NEC clearances"],
  ["02", "Commercial office", "Lighting, power, panel schedules"],
  ["03", "Campus equipment", "DWG to Revit, Python QA"],
  ["04", "Facilities handover", "Shared coordinates, IFC4"],
];

export default function Showreel() {
  const video = useRef(null);

  // Play silently while on screen, pause when scrolled away; never autoplay for reduced motion.
  useEffect(() => {
    const el = video.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const io = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) el.play().catch(() => {});
      else el.pause();
    }, { threshold: 0.4 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <Section id="showreel" alt kicker="Showreel" title="My work in 40 seconds"
      lead="Four projects, from electrical distribution and panel schedules to campus equipment models and facilities handover.">
      <div className="reel">
        <Reveal className="reel__frame">
          <video
            ref={video}
            src="/assets/video/portfolio-showreel-bright.mp4"
            poster="/assets/video/showreel-poster.jpg"
            width="1920"
            height="1080"
            muted
            loop
            playsInline
            controls
            preload="metadata"
            aria-label="Showreel of Harrison Farber's BIM projects"
          />
        </Reveal>
        <ol className="reel__list">
          {HIGHLIGHTS.map(([n, title, text]) => (
            <Reveal as="li" key={n}>
              <span className="reel__n">{n}</span>
              <div><strong>{title}</strong><span>{text}</span></div>
            </Reveal>
          ))}
        </ol>
      </div>
    </Section>
  );
}
