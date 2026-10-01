import Section, { Reveal } from "./Section.jsx";

const LOOP = [
  ["Detect", "Electrical vs. mechanical and structural in Navisworks"],
  ["Review", "Group, assign and prioritize in the clash report"],
  ["Resolve", "Reroute tray or conduit in Revit with the design team"],
  ["Re-run", "Refresh the federated model and test until clear"],
];

const PRINCIPLES = [
  ["Buildable", "What is modeled can be built: clearances, elevations and supports included."],
  ["Clean families", "Families and parameters that match the real equipment record."],
  ["Consistent standards", "Setup checklist, naming and LOD rules on every project."],
  ["Disciplined QA/QC", "Every model checked before it is accepted, with automated rules."],
  ["Aligned", "Shared coordinates so every discipline lands in the same place."],
];

export default function Coordination() {
  return (
    <Section id="coordination" alt kicker="Coordination & QA" title="Clashes solved before they reach site"
      lead="As BIM Coordinator at FMX I federate discipline models across multi-building campuses, run clash detection and track every issue to resolution with design teams.">
      <div className="coord">
        <Reveal className="photo coord__photo">
          <img src="/assets/images/stock/site-2.jpg" width="1024" height="681" alt="Two engineers in high-visibility jackets checking construction drawings" loading="lazy" />
          <span className="photo__tag">Coordination review</span>
        </Reveal>
        <div className="coord__side">
          <Reveal className="card clash" aria-label="Animation: a cable tray clashing with a steel beam is rerouted below it">
            <p className="tag">Clash test / Cable tray × Steel beam</p>
            <svg className="clash__svg" viewBox="0 0 320 120" aria-hidden="true">
              <text x="10" y="34" className="clash__lbl">STEEL BEAM</text>
              <rect x="10" y="42" width="300" height="22" rx="3" className="clash__beam" />
              <path className="clash__pipe" d="M20 53H300" />
              <circle className="clash__ring" cx="160" cy="53" r="14" />
            </svg>
            <span className="status"><span className="status__bad">Clash detected</span><span className="status__ok">Rerouted · re-run clear</span></span>
          </Reveal>
          <Reveal as="ol" className="loop">
            {LOOP.map(([t, d]) => <li key={t}><strong>{t}</strong><span>{d}</span></li>)}
          </Reveal>
        </div>
      </div>
      <h3 className="subhead">Working principles</h3>
      <div className="grid grid--5">
        {PRINCIPLES.map(([t, d], i) => (
          <Reveal as="article" className="card principle" key={t}>
            <span className="n">{String(i + 1).padStart(2, "0")}</span>
            <h4>{t}</h4>
            <p>{d}</p>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
