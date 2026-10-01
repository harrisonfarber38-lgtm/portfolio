export const LINKEDIN = "https://www.linkedin.com/in/harrison-farber-7b383943b";
export const EMAIL = "harrisonfarber38@gmail.com";

const SKILLS = ["Revit Electrical", "Navisworks Manage", "MEP coordination", "Clash detection", "Panel schedules", "IFC / COBie"];

export default function Hero() {
  return (
    <section className="hero">
      <div className="wrap">
        <div className="hero__grid">
          <div>
            <p className="kicker">BIM Coordinator · Overland Park, Kansas</p>
            <h1>BIM models <em>that can be built.</em></h1>
            <p className="hero__lead">
              I'm Harrison Farber, a BIM professional with 8 years of hands-on Revit experience, now
              a BIM Coordinator at FMX. I build detailed electrical Revit models from design intent and
              construction documents (equipment, lighting and devices, circuiting, panel schedules,
              conduit and cable tray), then coordinate them against mechanical and structural trades
              in Navisworks.
            </p>
            <ul className="chips" aria-label="Core skills">
              {SKILLS.map((s) => <li key={s}>{s}</li>)}
            </ul>
            <div className="hero__actions">
              <a className="btn btn--primary" href="#projects">View projects</a>
              <a className="btn btn--play" href="#showreel"><span aria-hidden="true">▶</span> Watch showreel</a>
              <a className="btn" href={`mailto:${EMAIL}`}>Email me</a>
              <a className="btn" href={LINKEDIN} target="_blank" rel="noopener noreferrer">LinkedIn ↗</a>
            </div>
          </div>

          <div className="hero__visual">
            <div className="photo hero__photo">
              <img src="/assets/images/stock/site-1.jpg" width="1024" height="681" alt="Engineers in hard hats reviewing drawings on a construction site" fetchPriority="high" />
            </div>
            <div className="float float--tl" aria-hidden="true">
              <span className="tag">Federated model</span>
              <div className="float__row"><span className="disc">ELEC</span><span className="disc">MECH</span><span className="disc">STR</span></div>
            </div>
            <div className="float float--br" aria-hidden="true">
              <span className="tag">Clash test</span>
              <strong>Cable tray × Steel beam</strong>
              <span className="status"><span className="status__bad">Hard clash</span><span className="status__ok">Rerouted · re-run clear</span></span>
            </div>
          </div>
        </div>

        <dl className="stats">
          <div><dt>Revit experience</dt><dd>8 <small>years hands-on</small></dd></div>
          <div><dt>Current role</dt><dd>BIM <small>Coordinator · FMX</small></dd></div>
          <div><dt>Model detail</dt><dd>LOD <small>300–400</small></dd></div>
          <div><dt>Specialty</dt><dd>Electrical <small>+ MEP coordination</small></dd></div>
        </dl>
      </div>
    </section>
  );
}
