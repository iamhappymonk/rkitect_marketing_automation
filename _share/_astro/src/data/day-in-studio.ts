// A single Tuesday in the studio — narrative timeline for /v2/ home.
// Six stamps. Time · what happens · who did it.
export type StudioMoment = {
  time: string;
  headline: string;
  body: string;
  role: string;
};

export const dayInStudio: StudioMoment[] = [
  {
    time: '09:00',
    headline: 'Brief in.',
    body: 'Client emails the kitchen revision. Bhavish forwards it to the studio.',
    role: 'Principal Architect',
  },
  {
    time: '10:30',
    headline: 'Scheme drafted.',
    body: 'Plan Drafter updates the plan. Space Planner adjusts the programme.',
    role: 'Plan Drafter · Space Planner',
  },
  {
    time: '12:00',
    headline: 'Materials proposed.',
    body: 'Materials Specialist swaps the floor — three finish options, paged.',
    role: 'Materials Specialist',
  },
  {
    time: '14:00',
    headline: 'Rendered.',
    body: 'Renderer ships four views. Lighting Designer locks the evening warm-light read.',
    role: 'Renderer · Lighting Designer',
  },
  {
    time: '16:00',
    headline: 'Pin-up.',
    body: 'Bhavish marks up two options. Redlines back to the studio.',
    role: 'Principal Architect',
  },
  {
    time: '17:30',
    headline: 'Revisions back.',
    body: 'Two corrected renders. Ready for the client tomorrow.',
    role: 'Renderer',
  },
];
