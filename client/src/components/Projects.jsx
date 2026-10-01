import { useState } from "react";
import { getProjects, useApi } from "../api.js";
import Section, { Reveal } from "./Section.jsx";
import Status from "./Status.jsx";

const FILTERS = [["all", "All"], ["professional", "Professional · FMX"], ["independent", "Independent"]];

export default function Projects({ onOpenImage }) {
  const { data, error, loading } = useApi(getProjects);
  const [filter, setFilter] = useState("all");
  const shown = (data || []).filter((p) => filter === "all" || p.type === filter);

  return (
    <Section id="projects" kicker="Selected projects" title="Projects"
      lead="Professional work at FMX and independent electrical models. Each project shows the drawings, schedules and reports it delivered.">
      <div className="filters" role="group" aria-label="Filter projects">
        {FILTERS.map(([key, label]) => (
          <button key={key} className={`filter${filter === key ? " is-active" : ""}`} aria-pressed={filter === key} onClick={() => setFilter(key)}>
            {label}
          </button>
        ))}
      </div>
      <Status loading={loading} error={error} what="projects" />
      {shown.map((p, i) => <Project key={p.slug} project={p} flip={i % 2 === 1} onOpenImage={onOpenImage} />)}
    </Section>
  );
}

function Project({ project: p, flip, onOpenImage }) {
  const all = [p.cover, ...p.images];
  const open = (i) => onOpenImage(all, i);
  return (
    <Reveal as="article" className={`project${flip ? " project--flip" : ""}`} id={p.slug}>
      <div className="media">
        <button className="media__cover" onClick={() => open(0)} aria-label={`View larger: ${p.cover.alt}`}>
          <img src={p.cover.src} width={p.cover.width} height={p.cover.height} alt={p.cover.alt} loading="lazy" />
          <span className="photo__tag">{p.cover.caption}</span>
        </button>
        <div className="media__views">
          {p.images.map((im, i) => (
            <button key={im.src} className={im.kind === "diagram" ? "is-diagram" : undefined} onClick={() => open(i + 1)} aria-label={`View larger: ${im.alt}`}>
              <img src={im.src} width={im.width} height={im.height} alt={im.alt} loading="lazy" />
              <span className="photo__tag">{im.caption}</span>
            </button>
          ))}
        </div>
      </div>
      <div className="project__body">
        <p className="tag">{p.context} · {p.year}</p>
        <h3>{p.name}</h3>
        <p className="project__sub">{p.tagline}</p>
        <dl className="meta">
          {p.facts.map((f) => <div key={f.label}><dt>{f.label}</dt><dd>{f.value}</dd></div>)}
        </dl>
        <ul className="highlights">{p.highlights.map((h) => <li key={h}>{h}</li>)}</ul>
        <p className="label">Skills shown</p>
        <ul className="pills">{p.skills.map((x) => <li key={x}>{x}</li>)}</ul>
      </div>
    </Reveal>
  );
}
