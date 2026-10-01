import { useCallback, useState } from "react";
import Nav from "./components/Nav.jsx";
import Hero from "./components/Hero.jsx";
import Showreel from "./components/Showreel.jsx";
import Skills from "./components/Skills.jsx";
import Projects from "./components/Projects.jsx";
import Workflow from "./components/Workflow.jsx";
import { Education, Experience } from "./components/Experience.jsx";
import Coordination from "./components/Coordination.jsx";
import Contact from "./components/Contact.jsx";
import Footer from "./components/Footer.jsx";
import Lightbox from "./components/Lightbox.jsx";

export default function App() {
  // the lightbox shows one project's images at a time
  const [viewer, setViewer] = useState(null);
  const openViewer = useCallback((images, index) => setViewer({ images, index }), []);

  return (
    <>
      <a className="skip" href="#main">Skip to content</a>
      <Nav />
      <main id="main">
        <Hero />
        <Showreel />
        <Skills />
        <Projects onOpenImage={openViewer} />
        <Experience />
        <Workflow />
        <Coordination />
        <Education />
        <Contact />
      </main>
      <Footer />
      <Lightbox viewer={viewer} onChange={setViewer} />
    </>
  );
}
