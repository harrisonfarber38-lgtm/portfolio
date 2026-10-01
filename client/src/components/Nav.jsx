import { useEffect, useState } from "react";
import { useActiveSection } from "../hooks.js";

const LINKS = [
  ["showreel", "Showreel"],
  ["skills", "Skills"],
  ["projects", "Projects"],
  ["experience", "Experience"],
  ["coordination", "Coordination"],
  ["education", "Education"],
];
const IDS = [...LINKS.map(([id]) => id), "contact"];

export default function Nav() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const active = useActiveSection(IDS);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    const onKey = (e) => e.key === "Escape" && setOpen(false);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  return (
    <header className={`nav${scrolled ? " is-scrolled" : ""}`} id="top">
      <div className="wrap nav__inner">
        <a className="brand" href="#top" aria-label="Harrison Farber, home">
          <span className="brand__mark" aria-hidden="true">HF</span>
          <span className="brand__text"><strong>Harrison Farber</strong><span>BIM Designer · Coordinator</span></span>
        </a>
        <button className="nav__toggle" aria-expanded={open} aria-controls="nav-links" aria-label="Menu" onClick={() => setOpen(!open)}>
          <span /><span />
        </button>
        <nav id="nav-links" className={`nav__links${open ? " is-open" : ""}`} aria-label="Sections" onClick={(e) => e.target.closest("a") && setOpen(false)}>
          {LINKS.map(([id, label]) => (
            <a key={id} href={`#${id}`} className={active === id ? "is-current" : undefined}>{label}</a>
          ))}
          <a href="#contact" className="nav__cta">Get in touch</a>
        </nav>
      </div>
    </header>
  );
}
