/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Main background palette
        dark: {
          DEFAULT: '#0F1A3F',
          700:     '#162038',
          800:     '#1A2B52',
          900:     '#141D33',
          950:     '#0a1128',
        },
        // Primary purple (matches Tailwind violet-600 = #7C3AED exactly)
        brand: {
          purple: '#7C3AED',
          blue:   '#3B82F6',
          teal:   '#06B6D4',
        },
      },
      fontFamily: {
        sans:  ['var(--font-poppins)', 'system-ui', 'sans-serif'],
        serif: ['var(--font-playfair)', 'Georgia', 'serif'],
      },
      backgroundImage: {
        'gradient-hero':    'radial-gradient(ellipse 80% 80% at 50% -20%, rgba(124,58,237,0.18) 0%, transparent 65%), radial-gradient(ellipse 60% 60% at 80% 60%, rgba(59,130,246,0.10) 0%, transparent 65%)',
        'gradient-section': 'radial-gradient(ellipse 60% 60% at 10% 80%, rgba(124,58,237,0.10) 0%, transparent 60%)',
      },
      rotate: {
        '60': '60deg',
        '70': '70deg',
      },
      transitionDuration: {
        '2000': '2000ms',
      },
      brightness: {
        '130': '1.3',
        '135': '1.35',
        '140': '1.4',
      },
      animation: {
        'blob':          'blob 8s infinite',
        'scroll-left':   'scroll-left 30s linear infinite',
        'scroll-right':  'scroll-right 30s linear infinite',
        'glow-pulse':    'glow-pulse 2.5s ease-in-out infinite',
        'float':         'float 3s ease-in-out infinite',
        'spotlight':     'spotlight 2s ease .75s 1 forwards',
        'spin-slow':     'spin 3s linear infinite',
      },
      keyframes: {
        blob:            { '0%,100%': { transform: 'translate(0,0) scale(1)' }, '33%': { transform: 'translate(30px,-50px) scale(1.1)' }, '66%': { transform: 'translate(-20px,20px) scale(0.9)' } },
        'scroll-left':   { '0%': { transform: 'translateX(0)' },   '100%': { transform: 'translateX(-50%)' } },
        'scroll-right':  { '0%': { transform: 'translateX(-50%)' },'100%': { transform: 'translateX(0)' } },
        'glow-pulse':    { '0%,100%': { boxShadow: '0 0 20px rgba(124,58,237,0.25)' }, '50%': { boxShadow: '0 0 50px rgba(124,58,237,0.55)' } },
        float:           { '0%,100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-8px)' } },
        spotlight:       { '0%': { opacity: '0', transform: 'translate(-72%, -62%) scale(0.5)' }, '100%': { opacity: '1', transform: 'translate(-50%, -40%) scale(1)' } },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
