export function LogoStrip() {
  const STATS = [
    { value: '22', label: 'Specialized agents' },
    { value: '200+', label: 'Native integrations' },
    { value: '5 min', label: 'Time to first deploy' },
    { value: 'SOC 2', label: 'Type II certified' },
    { value: '24/7', label: 'Always running' },
    { value: '$0', label: 'To get started' },
  ]

  return (
    <section
      style={{
        paddingTop: '2rem',
        paddingBottom: '2rem',
        borderTop: '1px solid oklch(0.97 0 0 / 0.08)',
        borderBottom: '1px solid oklch(0.97 0 0 / 0.08)',
        background: 'oklch(0.18 0 0)',
      }}
    >
      <div
        style={{
          maxWidth: '80rem',
          margin: '0 auto',
          padding: '0 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem 1.5rem',
        }}
      >
        {STATS.map((stat, i) => (
          <div
            key={stat.label}
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '0.5rem',
            }}
          >
            <span
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: '1.125rem',
                color: 'oklch(0.97 0 0)',
                letterSpacing: '-0.02em',
              }}
            >
              {stat.value}
            </span>
            <span
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: '0.8rem',
                color: 'oklch(0.55 0 0)',
              }}
            >
              {stat.label}
            </span>
            {i < STATS.length - 1 && (
              <span
                aria-hidden="true"
                style={{
                  marginLeft: '1rem',
                  color: 'oklch(0.30 0 0)',
                  fontSize: '0.75rem',
                }}
              >
                ·
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
