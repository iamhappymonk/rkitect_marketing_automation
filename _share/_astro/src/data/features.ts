// 12 capabilities grouped by 5 phases. /v2/product/ page.
// Vocabulary stays in architect dictionary. "Feature" used only as a structural label.
export type Capability = {
  n: string;
  name: string;
  body: string;
  fires: string;
};

export type Phase = {
  key: string;
  label: string;
  intro: string;
  capabilities: Capability[];
};

export const phases: Phase[] = [
  {
    key: 'brief',
    label: 'Phase one · Brief',
    intro: 'The studio takes whatever you have. Sketch, model, prompt, photo.',
    capabilities: [
      {
        n: '01',
        name: 'Brief Reader',
        body: 'Reads written briefs in studio vocabulary. Asks the questions a good associate would.',
        fires: 'Every new project.',
      },
      {
        n: '02',
        name: 'Multi-Input Intake',
        body: 'Hand sketch · site photo · floor plan · .dwg · .dxf · .skp · 3D model · written brief. The Principal Architect routes based on what you bring.',
        fires: 'Project kick-off.',
      },
      {
        n: '03',
        name: 'Site + Programme Reading',
        body: 'Extracts site constraints and programme from your inputs. Spaces named and sized before the line work starts.',
        fires: 'Pre-design.',
      },
    ],
  },
  {
    key: 'scheme',
    label: 'Phase two · Scheme',
    intro: 'Plans, sections, programme. Drafted by the Plan Drafter, set by the Space Planner.',
    capabilities: [
      {
        n: '04',
        name: 'Plan Drafter',
        body: 'Auto-drafts plans and sections from sketch, CAD, or SKP. Holds drafting standards: scale, line weight, dimensioning.',
        fires: 'Schematic and design development.',
      },
      {
        n: '05',
        name: 'Space Planner',
        body: 'Sets programme, adjacencies, parametric structure. Spaces named and sized to fit the brief.',
        fires: 'Pre-design and schematic.',
      },
    ],
  },
  {
    key: 'render',
    label: 'Phase three · Render',
    intro: 'Photoreal output. Multiple styles, multiple angles, multiple model passes — whichever the brief calls for.',
    capabilities: [
      {
        n: '06',
        name: 'Multi-Style Render',
        body: 'Switch architectural styles per pass. Modern · minimalist · japandi · brutalist · mid-century · neoclassical. Style library extends with project memory.',
        fires: 'Design development through pin-up.',
      },
      {
        n: '07',
        name: 'Multi-Angle + Hero Views',
        body: 'Multi-angle decks, hero shots, isometric, low-angle, plan-top, elevation. Camera presets calibrated for client review.',
        fires: 'Design development through pin-up.',
      },
      {
        n: '08',
        name: 'Multi-Model Routing',
        body: 'FAL · Google · Anthropic · OpenAI — routes the render through the best model for the input and style. The architect does not pick the model. The studio does.',
        fires: 'Every render pass.',
      },
    ],
  },
  {
    key: 'revision',
    label: 'Phase four · Revision',
    intro: 'Click any element. Swap the material. The render stays.',
    capabilities: [
      {
        n: '09',
        name: 'Auto-Segment + Click-to-Edit',
        body: 'Auto-Segment identifies every rendered element first. You click second. Material, finish, fixture, or object swaps without re-rendering the scene. No manual masking. No prompt rewriting.',
        fires: 'Revision rounds.',
      },
      {
        n: '10',
        name: 'Background Render Queue',
        body: 'Queue dozens of revision variations. Background renders run while you keep working. Pick the winners at pin-up.',
        fires: 'Revision rounds and pin-up prep.',
      },
    ],
  },
  {
    key: 'studio',
    label: 'Phase five · Studio',
    intro: 'The studio works like a studio. Memory across the project. Architect signs off at every gate.',
    capabilities: [
      {
        n: '11',
        name: 'Project Memory',
        body: 'Brief, programme, spaces, finishes, revisions, redlines — carried across sessions. Reopen the project tomorrow without re-briefing the team.',
        fires: 'Every session.',
      },
      {
        n: '12',
        name: 'Approval Gates',
        body: 'Every phase routes back to you before the next one opens. The studio proposes. The architect decides. No black-box output.',
        fires: 'Every phase transition.',
      },
    ],
  },
];
