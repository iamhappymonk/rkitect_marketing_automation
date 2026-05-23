/** @type {import('tailwindcss').Config} */
// Tokens extracted from _share/landing.css :root. OKLCH per impeccable mandate.
// See DESIGN-SYSTEM.md for full extraction notes.
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,vue,svelte,md,mdx}'],
  theme: {
    extend: {
      colors: {
        // Surfaces — paper palette, tinted toward warm cream (hue 70)
        paper: 'oklch(0.985 0.003 70)',
        'paper-elevated': 'oklch(0.995 0.003 70)',
        'paper-muted': 'oklch(0.965 0.004 70)',
        // Text — ink palette
        ink: 'oklch(0.22 0.01 70)',
        'ink-soft': 'oklch(0.42 0.01 70)',
        'ink-mute': 'oklch(0.55 0.01 70)',
        // Borders / hairlines
        rule: 'oklch(0.9 0.005 70)',
        'rule-hover': 'oklch(0.82 0.006 70)',
        // Redline accent — used SPARINGLY (10% rule)
        redline: 'oklch(0.55 0.18 25)',
        'redline-hover': 'oklch(0.49 0.18 25)',
        'redline-light': 'oklch(0.95 0.04 25)',
        // Blueprint blue — for ink-stamps + cohort marks
        blueprint: 'oklch(0.32 0.07 240)',
        'blueprint-hover': 'oklch(0.27 0.07 240)',
        'blueprint-light': 'oklch(0.94 0.03 240)',
      },
      fontFamily: {
        display: ['Spectral', 'Iowan Old Style', 'Georgia', 'serif'],
        sans: ['Switzer', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['Inconsolata', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1.4' }],
        xs: ['0.75rem', { lineHeight: '1.5' }],
        sm: ['0.8125rem', { lineHeight: '1.55' }],
        base: ['0.9375rem', { lineHeight: '1.55' }],
        md: ['1rem', { lineHeight: '1.55' }],
        lg: ['1.1875rem', { lineHeight: '1.45' }],
        xl: ['1.5rem', { lineHeight: '1.3' }],
        '2xl': ['1.875rem', { lineHeight: '1.2' }],
        '3xl': ['2.375rem', { lineHeight: '1.1' }],
        '4xl': ['3rem', { lineHeight: '1.05' }],
        'fluid-xl': ['clamp(2rem, 1.4rem + 2.4vw, 3.5rem)', { lineHeight: '1.02' }],
        'fluid-2xl': ['clamp(2.75rem, 1.8rem + 4.6vw, 5.5rem)', { lineHeight: '1.02' }],
        'fluid-3xl': ['clamp(3.5rem, 2.2rem + 6vw, 7rem)', { lineHeight: '1.02' }],
      },
      letterSpacing: {
        eyebrow: '0.18em',
        tightish: '-0.022em',
      },
      spacing: {
        // 4pt scale
        xs: '0.5rem',
        sm: '0.75rem',
        md: '1rem',
        lg: '1.5rem',
        xl: '2rem',
        '2xl': '3rem',
        '3xl': '4rem',
        '4xl': '6rem',
        '5xl': '8rem',
      },
      maxWidth: {
        prose: '60ch',
        page: '1200px',
      },
      transitionTimingFunction: {
        'out-quint': 'cubic-bezier(0.22, 1, 0.36, 1)',
        'out-back': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'out-soft': 'cubic-bezier(0.2, 0.7, 0.2, 1)',
      },
      boxShadow: {
        card: '0 1px 0 oklch(0 0 0 / 0.04)',
        'card-hover': '0 1px 2px oklch(0 0 0 / 0.06), 0 1px 0 oklch(0 0 0 / 0.04)',
        'card-elevated': '0 4px 16px oklch(0 0 0 / 0.08), 0 1px 0 oklch(0 0 0 / 0.04)',
      },
    },
  },
  plugins: [],
};
