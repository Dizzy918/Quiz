/**
 * Heraldic shields used as player avatars. The key is what the API stores,
 * the name is what a player reads.
 */
export const SHIELDS = [
  { key: 'knight-1', name: 'Орденът', field: '#8f2f23', metal: '#e7d8ae' },
  { key: 'knight-2', name: 'Мечовете', field: '#2f4a6d', metal: '#e7d8ae' },
  { key: 'knight-3', name: 'Кулата', field: '#3c5a42', metal: '#e7d8ae' },
  { key: 'knight-4', name: 'Короната', field: '#4a3763', metal: '#e7d8ae' },
]

export const AVATAR_KEYS = SHIELDS.map((shield) => shield.key)

const SHIELD_OUTLINE = 'M6 5 H58 V30 C58 47 47 57 32 62 C17 57 6 47 6 30 Z'

function Charge({ shieldKey, metal }) {
  switch (shieldKey) {
    case 'knight-2':
      return (
        <g stroke={metal} strokeWidth="3" strokeLinecap="round" fill="none">
          <path d="M20 20 L44 44" />
          <path d="M44 20 L20 44" />
          <path d="M16 24 L24 16" />
          <path d="M40 16 L48 24" />
        </g>
      )
    case 'knight-3':
      return (
        <g fill={metal}>
          <path d="M22 26 h4 v-5 h4 v5 h4 v-5 h4 v5 h4 v8 h-2 v14 h-16 v-14 h-2 z" />
          <rect x="29" y="40" width="6" height="8" fill="#3c5a42" />
        </g>
      )
    case 'knight-4':
      return (
        <g fill={metal}>
          <path d="M18 40 L18 22 L26 30 L32 18 L38 30 L46 22 L46 40 Z" />
          <rect x="18" y="43" width="28" height="5" />
        </g>
      )
    default:
      return (
        <g fill={metal}>
          <path d="M32 16 L48 34 L41 34 L32 24 L23 34 L16 34 Z" />
          <circle cx="23" cy="45" r="3.5" />
          <circle cx="32" cy="48" r="3.5" />
          <circle cx="41" cy="45" r="3.5" />
        </g>
      )
  }
}

export default function Shield({ avatarKey, size = 44 }) {
  const shield = SHIELDS.find((item) => item.key === avatarKey) ?? SHIELDS[0]

  return (
    <svg
      className="shield"
      width={size}
      height={size}
      viewBox="0 0 64 68"
      role="img"
      aria-label={`Герб ${shield.name}`}
    >
      <path d={SHIELD_OUTLINE} fill={shield.field} />
      <Charge shieldKey={shield.key} metal={shield.metal} />
      <path
        d={SHIELD_OUTLINE}
        fill="none"
        stroke="#2b2118"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
    </svg>
  )
}
