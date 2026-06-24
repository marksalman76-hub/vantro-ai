const COMPANIES = [
  'Northwind',
  'Cleardesk',
  'Lumen',
  'Stacksmith',
  'Halden',
  'Tidalflow',
  'Vertex',
  'Quanta',
]

export function LogoStrip() {
  return (
    <section
      style={{
        paddingTop: '3rem',
        paddingBottom: '3rem',
        borderTop: '1px solid oklch(0.97 0 0 / 0.08)',
        borderBottom: '1px solid oklch(0.97 0 0 / 0.08)',
        background: 'oklch(0.20 0 0 / 0.30)',
        overflow: 'hidden',
      }}
    >
      <p
        style={{
          textAlign: 'center',
          fontSize: '0.875rem',
          fontFamily: "'JetBrains Mono', monospace",
          letterSpacing: '0.12em',
          color: 'oklch(0.70 0 0)',
          marginBottom: '1.5rem',
          textTransform: 'uppercase',
          margin: '0 0 1.5rem 0',
        }}
      >
        Trusted by operators at fast-moving teams
      </p>

      <div
        className="marquee-row"
        style={{ overflow: 'hidden', position: 'relative' }}
      >
        <div
          className="marquee-track"
          style={{
            display: 'flex',
            animation: 'marquee 35s linear infinite',
            width: 'max-content',
          }}
        >
          {/* First pass */}
          {COMPANIES.map((name) => (
            <span
              key={`a-${name}`}
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.875rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'oklch(0.97 0 0)',
                marginLeft: '2rem',
                marginRight: '2rem',
                opacity: 0.6,
                transition: 'opacity 0.2s ease',
                cursor: 'default',
                userSelect: 'none',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLSpanElement).style.opacity = '1'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLSpanElement).style.opacity = '0.6'
              }}
            >
              {name}
            </span>
          ))}
          {/* Second pass for seamless loop */}
          {COMPANIES.map((name) => (
            <span
              key={`b-${name}`}
              aria-hidden="true"
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '0.875rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                color: 'oklch(0.97 0 0)',
                marginLeft: '2rem',
                marginRight: '2rem',
                opacity: 0.6,
                transition: 'opacity 0.2s ease',
                cursor: 'default',
                userSelect: 'none',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                ;(e.currentTarget as HTMLSpanElement).style.opacity = '1'
              }}
              onMouseLeave={(e) => {
                ;(e.currentTarget as HTMLSpanElement).style.opacity = '0.6'
              }}
            >
              {name}
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}
