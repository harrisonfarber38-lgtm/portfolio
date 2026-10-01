import Section, { Reveal } from "./Section.jsx";

// How Harrison runs a model from intake to handover (from the FMX role descriptions).
const STEPS = [
  ["Align coordinates", "Set shared coordinates and survey / project base points so every discipline model sits in the same real-world position."],
  ["Model from design intent", "Build equipment, devices, circuits, conduit and cable tray from construction documents, one-lines and DWG backgrounds."],
  ["Families & parameters to standard", "Use standardized families with required parameters per equipment type, so every element matches its real-world asset."],
  ["QA/QC before acceptance", "Check equipment location, working clearances, panel and circuit data and model health; automated rules catch the rest."],
  ["Federate in Navisworks", "Combine electrical, mechanical, structural and architectural models across buildings."],
  ["Clash detection", "Run electrical vs. mechanical and structural tests; group and assign issues in clash reports.", true],
  ["Track to resolution", "Work each clash through with design teams, reroute in Revit and re-run until clear.", true],
  ["Issue & hand over", "Sheets, panel and equipment schedules, plus IFC4 export so equipment data reaches the facilities system."],
];

export default function Workflow() {
  return (
    <Section id="process" kicker="How I work" title="From model intake to handover"
      lead="The same disciplined sequence on every model: aligned, built to standard, checked, coordinated and handed over with its data intact.">
      <div className="process">
        <Reveal className="photo process__photo">
          <img src="/assets/images/stock/industrial-1.jpg" width="1800" height="1350" alt="Power cable double-stacked in an aluminum ladder cable tray" loading="lazy" />
          <span className="photo__tag">Cable tray</span>
        </Reveal>
        <ol className="steps">
          {STEPS.map(([title, text, loop], i) => (
            <Reveal as="li" key={title} className={loop ? "steps__loop" : ""}>
              <span className="steps__n">{String(i + 1).padStart(2, "0")}</span>
              <div><h3>{title}</h3><p>{text}</p></div>
            </Reveal>
          ))}
        </ol>
      </div>
    </Section>
  );
}
