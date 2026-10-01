import { useState } from "react";
import { sendMessage } from "../api.js";
import { EMAIL, LINKEDIN } from "./Hero.jsx";
import Section, { Reveal } from "./Section.jsx";

const EMPTY = { name: "", email: "", company: "", message: "", website: "" };

export default function Contact() {
  const [form, setForm] = useState(EMPTY);
  const [state, setState] = useState({ status: "idle", error: "", fields: {} });
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setState({ status: "sending", error: "", fields: {} });
    try {
      await sendMessage(form);
      setForm(EMPTY);
      setState({ status: "sent", error: "", fields: {} });
    } catch (err) {
      setState({ status: "error", error: err.message, fields: err.fields || {} });
    }
  }

  const field = (k, label, props = {}) => {
    const Tag = props.rows ? "textarea" : "input";
    const err = state.fields[k];
    return (
      <label className={`field${err ? " field--error" : ""}`}>
        <span>{label}</span>
        <Tag value={form[k]} onChange={set(k)} name={k} aria-invalid={!!err} aria-describedby={err ? `${k}-err` : undefined} {...props} />
        {err && <em id={`${k}-err`}>{err}</em>}
      </label>
    );
  };

  return (
    <Section id="contact" alt className="contact" center kicker="Model / Coordinate / Deliver" title="Let's build together"
      lead="Looking for a BIM Designer role delivering electrical models for commercial and industrial construction.">
      <div className="contact__grid">
        <div className="contact__cards">
          <div className="card contact__card"><p className="tag">Name</p><p className="contact__v">Harrison Farber</p><p className="muted">BIM Coordinator · Electrical BIM Designer</p></div>
          <div className="card contact__card"><p className="tag">Location</p><p className="contact__v">Overland Park, Kansas</p><p className="muted">Kansas · United States</p></div>
          <a className="card contact__card contact__card--link" href={LINKEDIN} target="_blank" rel="noopener noreferrer">
            <p className="tag">LinkedIn</p><p className="contact__v">Harrison Farber ↗</p><p className="muted">linkedin.com/in/harrison-farber-7b383943b</p>
          </a>
          <a className="card contact__card contact__card--link" href={`mailto:${EMAIL}`}>
            <p className="tag">Email</p><p className="contact__v">{EMAIL}</p><p className="muted">Click to send an email</p>
          </a>
        </div>
        <Reveal as="form" className="card form" onSubmit={submit} noValidate>
          <p className="tag">Send a message</p>
          {state.status === "sent" ? (
            <div className="form__done" role="status">
              <p className="contact__v">Thanks, message received.</p>
              <p className="muted">I'll get back to you by email.</p>
              <button type="button" className="btn" onClick={() => setState({ status: "idle", error: "", fields: {} })}>Send another</button>
            </div>
          ) : (
            <>
              <div className="form__row">
                {field("name", "Name", { required: true, maxLength: 100, autoComplete: "name" })}
                {field("email", "Email", { type: "email", required: true, maxLength: 200, autoComplete: "email" })}
              </div>
              {field("company", "Company (optional)", { maxLength: 150, autoComplete: "organization" })}
              {field("message", "Message", { rows: 5, required: true, minLength: 10, maxLength: 5000 })}
              {/* honeypot: hidden from people, filled by bots */}
              <input className="hp" tabIndex={-1} autoComplete="off" name="website" value={form.website} onChange={set("website")} aria-hidden="true" />
              {state.status === "error" && <p className="state state--error" role="alert">{state.error}</p>}
              <button className="btn btn--primary" disabled={state.status === "sending"}>
                {state.status === "sending" ? "Sending…" : "Send message"}
              </button>
            </>
          )}
        </Reveal>
      </div>
    </Section>
  );
}
