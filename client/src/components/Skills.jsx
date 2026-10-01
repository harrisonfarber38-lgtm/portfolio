import Section, { Reveal } from "./Section.jsx";

const icons = {
  elec: <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" />,
  model: <path d="M12 2 3 7v10l9 5 9-5V7l-9-5Zm0 0v10m0 0 9-5m-9 5-9-5" />,
  clash: <><circle cx="12" cy="12" r="8" /><path d="M4 12h16M12 4v16" /></>,
  docs: <path d="M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6" />,
  data: <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" /></>,
};

// From the resume's Technical Skills section.
const SKILLS = [
  ["elec", "Revit Electrical", "Detailed electrical models", ["Switchboards, panelboards and transformers", "Lighting fixtures and devices", "Circuiting, panel schedules and load classifications", "Conduit and cable tray with fittings"]],
  ["model", "Revit Modeling", "Families and model setup", ["Family creation and editing", "Shared and type parameters", "View templates, sheets and schedules", "Worksharing, shared coordinates, DWG backgrounds"]],
  ["clash", "MEP Coordination", "Navisworks Manage", ["Model federation across disciplines", "Clash detection and clash reports", "Autodesk Construction Cloud / BIM 360", "Model QA/QC at LOD 300–400"]],
  ["docs", "Construction Documents", "Reading and producing", ["Electrical drawings, one-lines and specifications", "Power and lighting plans", "Panel and equipment schedules on sheets"]],
  ["data", "Automation & Data", "Model data you can trust", ["Python model-validation scripts", "SQL", "IFC / COBie export", "Dynamo (developing)"]],
];

const SOFTWARE = [
  ["#1f6fd1", "R", "Autodesk Revit", "Electrical · MEP · families"],
  ["#2f9a54", "N", "Navisworks Manage", "Federation · clash detection"],
  ["#0b3d91", "A", "Autodesk Construction Cloud", "BIM 360 · model sharing"],
  ["#c62828", "D", "AutoCAD", "DWG backgrounds"],
  ["#3776ab", "Py", "Python & SQL", "Model data validation"],
  ["#6d28d9", "IFC", "IFC4 / COBie", "Facilities handover"],
];

export default function Skills() {
  return (
    <Section id="skills" kicker="Professional skills" title="What I bring to a project team">
      <div className="skills">
        <Reveal className="photo skills__photo">
          <img src="/assets/images/stock/industrial-3.jpg" width="1300" height="867" alt="Engineer standing at an electrical control panel" loading="lazy" />
          <span className="photo__tag">Model it so it can be built</span>
        </Reveal>
        <div>
          <p className="skills__about">
            Detailed electrical Revit models built from design intent and construction documents,
            coordinated against mechanical and structural trades so that what is modeled can be
            built. Known for clean families and parameters, consistent model standards and
            disciplined QA/QC.
          </p>
          <div className="grid grid--2">
            {SKILLS.map(([icon, title, sub, items]) => (
              <Reveal as="article" className="card skill" key={title}>
                <div className="skill__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{icons[icon]}</svg></div>
                <h3>{title}</h3>
                <p>{sub}</p>
                <ul className="ticks">{items.map((i) => <li key={i}>{i}</li>)}</ul>
              </Reveal>
            ))}
          </div>
          <ul className="software" aria-label="Software">
            {SOFTWARE.map(([c, k, name, sub]) => (
              <li key={name}><b style={{ background: c }}>{k}</b><span>{name}<small>{sub}</small></span></li>
            ))}
          </ul>
        </div>
      </div>
    </Section>
  );
}
