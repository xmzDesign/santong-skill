/**
 * BYAI Design System v1 — Tailwind v4 Configuration
 *
 * Usage:
 *   1. Copy this config to your project's tailwind.config.js
 *   2. Import tokens.css in your CSS entry: @import "./tokens/tokens.css";
 *   3. Use utility classes: bg-surface, text-fg-default, border-default, etc.
 */

module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,html}'],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      white: '#FFFFFF',

      // Primitive · Warm Grey
      'warm-grey': {
        50:  '#FAFAF7', 100: '#F4F2ED', 200: '#E8E4DB', 300: '#D4CEC1',
        400: '#A8A093', 500: '#7A7366', 600: '#5C564B', 700: '#3F3A32',
        800: '#2A2620', 900: '#1A1814', 950: '#0D0C0A',
      },
      // Primitive · Amber
      amber: {
        50:  '#FDF8EE', 100: '#FAEBCA', 200: '#F5D88F', 300: '#EFC257',
        400: '#E4A72E', 500: '#C88A1A', 600: '#A36E10', 700: '#7E560D',
        800: '#5E400B', 900: '#402C08',
      },
      // Primitive · Blue
      blue: {
        50:  '#EEF4FA', 100: '#D6E4F3', 200: '#A9C6E6', 300: '#78A5D5',
        400: '#4784C1', 500: '#2A69A8', 600: '#1E5189', 700: '#153E6B',
        800: '#0F2D4E', 900: '#0A1E34',
      },
      // Primitive · Red
      red: {
        50:  '#FCF1ED', 100: '#F8DACF', 200: '#EDB39F', 300: '#DD8469',
        400: '#CC5A3A', 500: '#B03E1E', 600: '#8F2E14', 700: '#6F220E',
        800: '#4F1809', 900: '#321005',
      },
      // Primitive · Yellow
      yellow: {
        50: '#FEF9E4', 100: '#FDEDA9', 300: '#F7CE2B', 500: '#D69E08',
        700: '#8A6402', 900: '#3D2C00',
      },
      // Primitive · Teal
      teal: { 100: '#D4EDE8', 400: '#2E9C8A', 600: '#1B6F62', 800: '#0E3D36' },
      // Primitive · Violet (Agent only)
      violet: { 50: '#F5F2FA', 100: '#E4DDF2', 400: '#7A5DB0', 600: '#5A3F94', 800: '#32215A' },

      // Semantic · Background
      'bg-canvas':          'var(--bg-canvas)',
      'bg-surface':         'var(--bg-surface)',
      'bg-surface-sunken':  'var(--bg-surface-sunken)',
      'bg-surface-subtle':  'var(--bg-surface-subtle)',
      'bg-hover':           'var(--bg-hover)',
      'bg-active':          'var(--bg-active)',
      'bg-selected':        'var(--bg-selected)',
      'bg-selected-strong': 'var(--bg-selected-strong)',
      'bg-disabled':        'var(--bg-disabled)',
      'bg-overlay':         'var(--bg-overlay)',
      'bg-inverse':         'var(--bg-inverse)',
      'bg-agent':           'var(--bg-agent-surface)',
      'bg-agent-trace':     'var(--bg-agent-trace)',

      // Semantic · Foreground
      'fg-default':    'var(--fg-default)',
      'fg-strong':     'var(--fg-strong)',
      'fg-muted':      'var(--fg-muted)',
      'fg-subtle':     'var(--fg-subtle)',
      'fg-disabled':   'var(--fg-disabled)',
      'fg-on-primary': 'var(--fg-on-primary)',
      'fg-on-danger':  'var(--fg-on-danger)',
      'fg-on-inverse': 'var(--fg-on-inverse)',
      'fg-link':       'var(--fg-link)',
      'fg-brand':      'var(--fg-brand)',
      'fg-agent':      'var(--fg-agent)',
    },

    borderColor: {
      DEFAULT:   'var(--border-default)',
      subtle:    'var(--border-subtle)',
      strong:    'var(--border-strong)',
      inverse:   'var(--border-inverse)',
      focus:     'var(--border-focus)',
      selected:  'var(--border-selected)',
      danger:    'var(--border-danger)',
      agent:     'var(--border-agent)',
      transparent: 'transparent',
    },

    fontFamily: {
      display: ['Fraunces', 'Instrument Serif', 'Georgia', 'serif'],
      sans:    ['Geist', 'Söhne', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      mono:    ['JetBrains Mono', 'Geist Mono', 'ui-monospace', 'monospace'],
      cjk:     ['Microsoft YaHei', '微软雅黑', 'PingFang SC', 'Source Han Sans CN', 'sans-serif'],
      body:    ['Geist', '-apple-system', 'BlinkMacSystemFont', 'Microsoft YaHei', 'sans-serif'],
      heading: ['Fraunces', 'Instrument Serif', 'Georgia', 'Microsoft YaHei', 'serif'],
    },

    fontSize: {
      'micro':      ['11px', { lineHeight: '14px', letterSpacing: '0.02em', fontWeight: '500' }],
      'caption':    ['12px', { lineHeight: '16px' }],
      'small':      ['13px', { lineHeight: '18px' }],
      'body':       ['14px', { lineHeight: '20px' }],
      'body-lg':    ['16px', { lineHeight: '24px' }],
      'h3':         ['18px', { lineHeight: '24px', fontWeight: '600' }],
      'h2':         ['22px', { lineHeight: '28px', letterSpacing: '-0.01em', fontWeight: '600' }],
      'h1':         ['28px', { lineHeight: '34px', letterSpacing: '-0.015em', fontWeight: '600' }],
      'display-l':  ['36px', { lineHeight: '40px', letterSpacing: '-0.02em', fontWeight: '500' }],
      'display-xl': ['48px', { lineHeight: '52px', letterSpacing: '-0.02em', fontWeight: '500' }],
    },

    fontWeight: {
      regular:  '400',
      medium:   '500',
      semibold: '600',
      bold:     '700',
    },

    spacing: {
      0:    '0',
      0.5:  '2px',
      1:    '4px',
      2:    '8px',
      3:    '12px',
      4:    '16px',
      5:    '20px',
      6:    '24px',
      8:    '32px',
      10:   '40px',
      12:   '48px',
      16:   '64px',
      20:   '80px',
      24:   '96px',
    },

    borderRadius: {
      none: '0',
      xs:   '2px',
      sm:   '4px',
      md:   '6px',
      lg:   '8px',
      xl:   '12px',
      '2xl': '16px',
      '3xl': '24px',
      full: '9999px',
      DEFAULT: '6px',
    },

    boxShadow: {
      none: 'none',
      xs:   'var(--shadow-xs)',
      sm:   'var(--shadow-sm)',
      md:   'var(--shadow-md)',
      lg:   'var(--shadow-lg)',
      xl:   'var(--shadow-xl)',
      focus:        'var(--shadow-focus-ring)',
      'focus-danger': 'var(--shadow-focus-ring-danger)',
    },

    transitionDuration: {
      instant: '0ms',
      fast:    '120ms',
      base:    '200ms',
      slow:    '320ms',
      slower:  '500ms',
      slowest: '800ms',
      DEFAULT: '200ms',
    },

    transitionTimingFunction: {
      linear:     'linear',
      out:        'cubic-bezier(0.25, 1, 0.5, 1)',
      'in-out':   'cubic-bezier(0.65, 0, 0.35, 1)',
      spring:     'cubic-bezier(0.34, 1.56, 0.64, 1)',
      anticipate: 'cubic-bezier(0.87, 0, 0.13, 1)',
      DEFAULT:    'cubic-bezier(0.25, 1, 0.5, 1)',
    },

    zIndex: {
      base:            '0',
      raised:          '10',
      dropdown:        '100',
      sticky:          '200',
      drawer:          '300',
      modal:           '400',
      popover:         '500',
      toast:           '600',
      'command-palette': '700',
      top:             '9999',
    },

    screens: {
      sm:  '640px',
      md:  '768px',
      lg:  '1024px',
      xl:  '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
    },
  },
  plugins: [],
};
