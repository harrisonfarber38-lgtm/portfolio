import { getProfile, useApi } from "../api.js";
import Section, { Reveal } from "./Section.jsx";
import Status from "./Status.jsx";

// "BIM skills progression" from the resume.
const PROGRESSION = [
  ["2018 – 2019", "Foundations", "Learned Revit and AutoCAD fundamentals: levels, views, sheets and schedules; built practice models to understand how buildings and systems are assembled in BIM."],
  ["2019 – 2023", "Building depth", "Kept developing Revit skills alongside an analyst career: families and parameters, worksharing, MEP systems, IFC export and Navisworks review."],
  ["2023 – 2024", "BIM Modeler", "Modeled buildings and equipment, including electrical panels, from DWG drawings and client Revit models; standardized families and parameters."],
  ["2024 – Present", "BIM Coordinator", "Lead model coordination: shared coordinates, federated MEP models, clash detection, model standards and a small team."],
  ["Next", "Electrical BIM Designer", "Delivering detailed, buildable electrical Revit models for commercial and industrial construction."],
];

export function Experience() {
  const { data, error, loading } = useApi(getProfile);
  return (
    <Section id="experience" alt kicker="Professional experience" title="Experience"
      lead="Over three years in professional BIM roles at FMX, on top of eight years of hands-on Revit.">
      <Status loading={loading} error={error} what="experience" />
      <ol className="timeline">
        {data?.experience.map((job) => (
          <Reveal as="li" className="job card" key={job.role + job.period}>
            <div className="job__head">
              <div>
                <h3>{job.role}</h3>
                <p className="job__org">{job.company} · {job.location}</p>
              </div>
              <span className="job__period">{job.period}</span>
            </div>
            {job.scope && <p className="job__scope">{job.scope}</p>}
            <ul className="ticks">{job.points.map((pt) => <li key={pt}>{pt}</li>)}</ul>
          </Reveal>
        ))}
      </ol>

      <h3 className="subhead">BIM skills progression</h3>
      <ol className="progress">
        {PROGRESSION.map(([period, title, text], i) => (
          <Reveal as="li" key={title} className={i === PROGRESSION.length - 1 ? "progress__next" : i === PROGRESSION.length - 2 ? "progress__now" : ""}>
            <span className="progress__period">{period}</span>
            <h4>{title}</h4>
            <p>{text}</p>
          </Reveal>
        ))}
      </ol>
    </Section>
  );
}

export function Education() {
  const { data } = useApi(getProfile);
  return (
    <Section id="education" kicker="Education" title="Education">
      <div className="edu">
        {data?.education.map((e) => (
          <Reveal as="article" className="card edu__card" key={e.school}>
            <div className="edu__icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M2 9l10-5 10 5-10 5L2 9Z" /><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5" /></svg>
            </div>
            <div>
              <h3>{e.school}</h3>
              <p className="edu__degree">{e.degree}</p>
            </div>
            <span className="job__period">{e.period}</span>
          </Reveal>
        ))}
        <Reveal as="article" className="card edu__card edu__card--self">
          <div className="edu__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2 3 7v10l9 5 9-5V7l-9-5Zm0 0v10m0 0 9-5m-9 5-9-5" /></svg>
          </div>
          <div>
            <h3>Self-directed BIM training</h3>
            <p className="edu__degree">Revit, AutoCAD, Navisworks, MEP systems and IFC, built up through practice models and independent projects since 2018</p>
          </div>
          <span className="job__period">2018 – Present</span>
        </Reveal>
      </div>
    </Section>
  );
}
