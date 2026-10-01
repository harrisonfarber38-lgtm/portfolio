// Portfolio content, taken from Harrison Farber's resume ("Harrison Farber - BIM Designer.docx").
// Loaded into MongoDB by seed.js (and served directly when running without a database).
//
// Images: `photo` entries are openly licensed (CC0) reference photos of the subject matter
// (see assets/images/stock/CREDITS.md); `diagram` entries are recreations of the deliverable
// type drawn to real CAD/Revit conventions by tools/build_diagrams.py. Neither is a client file.

const photo = (file, caption, alt, width, height) => ({
  src: `/assets/images/stock/${file}`, caption, alt, width, height, kind: "photo",
});
// Drawing sheets are ANSI D (2200 x 1424); report pages are 1700 x 1100.
const sheet = (file, caption, alt) => ({
  src: `/assets/images/diagrams/${file}`, caption, alt, width: 2200, height: 1424, kind: "diagram",
});
const report = (file, caption, alt) => ({
  src: `/assets/images/diagrams/${file}`, caption, alt, width: 1700, height: 1100, kind: "diagram",
});

export const projects = [
  {
    slug: "industrial-electrical-distribution",
    order: 1,
    type: "independent",
    context: "Independent project",
    year: "2025",
    name: "Industrial Facility — Electrical Distribution & Cable Tray Model",
    tagline: "Power distribution for a light-industrial production facility, modeled and coordinated to be buildable",
    facts: [
      { label: "Discipline", value: "Electrical" },
      { label: "LOD", value: "300–400" },
      { label: "Tools", value: "Revit · Navisworks" },
    ],
    highlights: [
      "Modeled the power distribution: service switchboard, step-down transformers, motor control center and distribution panelboards, with nameplate data in equipment parameters.",
      "Routed ladder cable tray and conduit runs with fittings and hangers at coordinated elevations; modeled NEC working-clearance zones in front of electrical equipment.",
      "Ran Navisworks clash detection against structural steel and process piping, and rerouted tray and conduit to clear every hard clash.",
      "Issued sheets with power plans, cable tray layout, an enlarged electrical room plan and equipment schedules.",
    ],
    skills: ["Electrical equipment", "Cable tray & conduit", "NEC clearances", "Clash detection", "Equipment schedules"],
    cover: photo("industrial-1.jpg", "Cable tray", "Heavy power cable double-stacked in an aluminum ladder cable tray", 1800, 1350),
    images: [
      sheet("industrial-one-line.svg", "E-601 One-line diagram", "One-line diagram: utility transformer, 3000A main switchboard, MCC-1, transformers T-1 and T-2, panelboards"),
      sheet("industrial-tray-plan.svg", "E-201 Cable tray & power plan", "Level 1 plan with ladder cable tray routing, tray tags with bottom elevations and conduit drops"),
      sheet("industrial-elec-room.svg", "E-401 Enlarged electrical room", "Enlarged electrical room plan with NEC 110.26 working-clearance zones in front of each piece of equipment"),
      sheet("industrial-3d-tray.svg", "E-701 3D coordination view", "3D view of cable tray offsetting under process piping, with trapeze hangers and steel beams"),
      report("industrial-clash-report.svg", "Navisworks clash report", "Navisworks clash report: tray and conduit versus structure and piping, 23 clashes resolved"),
      photo("industrial-2.jpg", "Panelboard", "Open panelboard with rows of circuit breakers", 1024, 576),
      photo("industrial-5.jpg", "Transformers", "Pad transformers and switching equipment at a power substation", 1300, 948),
      photo("industrial-8.jpg", "EMT conduit", "Lengths of EMT conduit and bending tools on a job-site rack", 1800, 1013),
      photo("industrial-6.jpg", "Process piping", "Stainless process piping and instruments in a production plant", 1024, 576),
    ],
  },
  {
    slug: "commercial-office-electrical",
    order: 2,
    type: "independent",
    context: "Independent project · Autodesk Snowdon Towers sample",
    year: "2025",
    name: "Commercial Office Building — Electrical Model",
    tagline: "Lighting and power for a multi-story office, circuited to panelboards with schedules straight from the model",
    facts: [
      { label: "Discipline", value: "Electrical" },
      { label: "Building", value: "Multi-story office" },
      { label: "Tools", value: "Revit Electrical" },
    ],
    highlights: [
      "Built the electrical model for a multi-story commercial office from Autodesk's Snowdon Towers sample project: lighting fixtures, receptacles, switches, panelboards and distribution equipment.",
      "Circuited lighting and power devices to panelboards, applied load classifications, and generated panel schedules directly from the model.",
      "Created view templates and sheets for lighting plans, power plans and panel schedules, set up for construction-document output.",
    ],
    skills: ["Lighting & devices", "Circuiting", "Panel schedules", "Load classifications", "View templates & sheets"],
    cover: photo("office-ext.jpg", "Commercial office", "Mid-rise commercial office building with brick and glass facade", 1024, 683),
    images: [
      sheet("office-panel-schedule.svg", "E-501 Panel schedule LP-3A", "Revit branch panel schedule LP-3A with circuits, phase loads and load classification totals"),
      sheet("office-lighting-plan.svg", "E-301 Lighting plan", "Level 3 lighting plan with fixtures circuited to LP-3A, homeruns and a fixture schedule"),
      sheet("office-power-plan.svg", "E-302 Power plan", "Level 3 power plan with receptacles, floor boxes, GFCI devices and homeruns to RP-3A"),
      photo("office-int.jpg", "Office lighting", "Open-plan office interior with ceiling light fixtures", 1536, 2048),
      photo("office-3.jpg", "Device installation", "Electrician installing a wall device", 960, 639),
      photo("office-4.jpg", "Floor box receptacles", "Power and USB receptacles set flush in a desk surface", 1536, 2048),
    ],
  },
  {
    slug: "campus-equipment-modeling",
    order: 3,
    type: "professional",
    context: "FMX · BIM Modeler",
    year: "2023 – 2024",
    name: "Multi-Building Campus Equipment Modeling",
    tagline: "Levels, rooms and building equipment modeled in place from client drawings, with automated QA",
    facts: [
      { label: "Scope", value: "Multiple campus buildings" },
      { label: "Source", value: "Client DWG plans" },
      { label: "Tools", value: "Revit · Python" },
    ],
    highlights: [
      "Modeled levels, rooms and building equipment (electrical panels, HVAC units, boilers) in their correct locations from client DWG floor plans across multiple campus buildings.",
      "Wrote QA rules (overlapping rooms, unplaced equipment, mismatched level IDs) that sharply reduced model-cleanup time per building.",
    ],
    skills: ["DWG to Revit", "Rooms & levels", "Equipment families", "Model QA/QC", "Python"],
    cover: photo("campus-1.jpg", "Campus building", "Low-rise school campus building under a clear sky", 1024, 683),
    images: [
      sheet("campus-equipment-plan.svg", "M-101 Equipment location plan", "Equipment location plan: boilers, chillers, switchboard, panels, pumps and AHU placed over the client DWG with Revit room tags"),
      report("campus-qa-report.svg", "QA script report", "Spreadsheet output of the Python QA script listing rule failures by building and element ID"),
      photo("campus-2.jpg", "Mechanical room", "Mechanical room with color-coded pipework and pumps", 1024, 702),
      photo("campus-3.jpg", "Boiler room", "Heating plant room with pumps and insulated pipework", 1024, 726),
      photo("campus-4.jpg", "Campus building", "Modern college campus building with glass facade", 1024, 679),
      photo("campus-5.jpg", "Campus building", "Three-story brick campus building", 1024, 680),
    ],
  },
  {
    slug: "bim-to-facilities-handover",
    order: 4,
    type: "professional",
    context: "FMX · BIM Coordinator",
    year: "2024 – 2025",
    name: "BIM-to-Facilities Model Handover Pilot",
    tagline: "Model-quality requirements and IFC4 export so equipment data reaches the facilities system without re-keying",
    facts: [
      { label: "Standard", value: "IFC4 · COBie" },
      { label: "Requirements", value: "LOD · parameters · coordinates" },
      { label: "Role", value: "BIM Coordinator" },
    ],
    highlights: [
      "Defined model-quality requirements (LOD, required parameters, coordinate setup) for every model entering the pilot.",
      "Set IFC4 export settings so equipment data, including electrical equipment, carries from Revit into the facilities system without re-keying.",
    ],
    skills: ["IFC4 export", "Model standards", "Shared coordinates", "Data mapping", "COBie"],
    cover: photo("handover-1.jpg", "Operations center", "Operations room with rows of monitors at workstations", 1200, 793),
    images: [
      report("handover-standards.svg", "BIM standards: LOD & parameters", "Standards page listing required parameters, LOD and IFC class for each equipment type, plus naming conventions"),
      report("handover-data-map.svg", "IFC4 export & data mapping", "IFC4 export settings, property-set mapping from Revit parameters and a verification sample"),
      sheet("handover-coordinates.svg", "G-002 Shared coordinates", "Campus site sheet showing survey point, project base point, true north and linked models by shared coordinates"),
      photo("industrial-4.jpg", "Equipment verification", "Inspector checking wiring inside an electrical panel", 1024, 768),
      photo("handover-2.jpg", "Equipment maintenance", "Technician servicing building equipment", 1024, 684),
      photo("handover-3.jpg", "Facilities inspection", "Technician in a hard hat inspecting equipment", 1300, 867),
    ],
  },
];

export const experience = [
  {
    company: "FMX",
    role: "BIM Coordinator",
    period: "Feb 2024 – Present",
    location: "New York, NY",
    scope: "Owns BIM coordination and model quality for client facilities: aligns and federates discipline models, resolves clashes with design teams, and sets the standards every model must meet.",
    points: [
      "Federate architectural and MEP Revit models in Navisworks across multi-building campuses; run clash detection between electrical, mechanical and structural elements and track each issue to resolution with design teams.",
      "Review electrical models against construction documents for correct equipment location, required working clearances, and complete panel and circuit data before acceptance.",
      "Set Revit shared coordinates and survey/project base points so every discipline model aligns in the same real-world position.",
      "Wrote the team's BIM standards: model setup checklist, naming conventions, required parameters and LOD requirements per equipment type, now the baseline for every new client project.",
      "Lead a small BIM team; act as the link between BIM, product and client stakeholders.",
    ],
  },
  {
    company: "FMX",
    role: "BIM Modeler",
    period: "Mar 2023 – Feb 2024",
    location: "New York, NY",
    scope: "Produced Revit models of buildings and their equipment from client drawings and models, and checked incoming models for accuracy before use.",
    points: [
      "Translated client DWG floor plans and construction documents into Revit models of levels, rooms and equipment, including electrical panels and distribution equipment, across multi-building campuses.",
      "Built and standardized equipment families and parameters so every modeled panel and unit matched its real-world asset record.",
      "Ran QA/QC on client Revit models: room boundaries, equipment parameters, coordinate placement and model health.",
      "Wrote Python scripts to validate model and equipment data, replacing hours of manual cleanup each week.",
    ],
  },
  {
    company: "Fenics US Treasuries",
    role: "Business Analyst",
    period: "Dec 2019 – Mar 2023",
    location: "New York, NY",
    scope: "",
    points: [
      "Analyzed trading data with SQL and Python and translated business requirements into reporting solutions with product and technology teams.",
    ],
  },
];

export const education = [
  { school: "Dartmouth College", degree: "A.B., Political Science and Government", period: "2015 – 2019" },
];
