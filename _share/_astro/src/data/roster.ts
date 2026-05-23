// Canonical brand-facing roster — Voice.md L46-59. Single source of truth.
// = 1 chief + 5 specialists.
export type RosterMember = {
  id: string;
  name: string;
  role: 'chief' | 'specialist';
  craft: string;
  active: string;
  leaves: string;
};

export const roster: RosterMember[] = [
  {
    id: 'principal',
    name: 'Principal Architect',
    role: 'chief',
    craft: 'Takes the brief, sets direction, routes the work, signs off at every gate.',
    active: 'First read of the brief, every review, every revision sign-off.',
    leaves: 'A direction the studio works against, and a redline on every set before it goes back.',
  },
  {
    id: 'plan-drafter',
    name: 'Plan Drafter',
    role: 'specialist',
    craft: 'Plans, sections, line work. Holds the drafting standards.',
    active: 'Schematic and design development.',
    leaves: 'Drafted plans and sections from a sketch, CAD import, or SKP model.',
  },
  {
    id: 'space-planner',
    name: 'Space Planner',
    role: 'specialist',
    craft: 'Programme, spaces, adjacencies, parametric structure.',
    active: 'Pre-design and schematic — before the line work hardens.',
    leaves: 'Spaces named and sized, adjacencies resolved, programme laid against the site.',
  },
  {
    id: 'renderer',
    name: 'Renderer',
    role: 'specialist',
    craft: 'Photoreal output. Multi-angle hero views. The render queue.',
    active: 'Design development through pin-up.',
    leaves: 'Hero shots, multi-angle decks, options for the client review.',
  },
  {
    id: 'materials',
    name: 'Materials Specialist',
    role: 'specialist',
    craft: 'Finishes, colors, palettes, fixtures, furniture spec.',
    active: 'Concept through revision rounds.',
    leaves: 'A specified palette per space — every finish callout the client will ask about.',
  },
  {
    id: 'lighting',
    name: 'Lighting Designer',
    role: 'specialist',
    craft: 'Natural and artificial light strategy. Atmosphere. Mood. Time of day.',
    active: 'Concept through revision rounds.',
    leaves: 'A lighting strategy per space — daylight reads, evening reads, fixture intent.',
  },
];
