import { useReveal } from "../hooks.js";

/** Standard section shell: kicker, gradient heading, optional lead. */
export default function Section({ id, kicker, title, lead, alt, center, className = "", children }) {
  return (
    <section className={`section${alt ? " section--alt" : ""} ${className}`} id={id} aria-labelledby={`${id}-h`}>
      <div className="wrap">
        <header className={`section__head${center ? " section__head--center" : ""}`}>
          <p className="kicker">{kicker}</p>
          <h2 id={`${id}-h`}>{title}</h2>
          {lead && <p className="section__lead">{lead}</p>}
        </header>
        {children}
      </div>
    </section>
  );
}

/** Any element that fades up when scrolled into view. */
export function Reveal({ as: Tag = "div", className = "", ...props }) {
  const [ref, cls] = useReveal();
  return <Tag ref={ref} className={`${cls} ${className}`} {...props} />;
}
