import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMagnifyingGlass, faClockRotateLeft } from '@fortawesome/free-solid-svg-icons'

interface Props {
  page: string
  onNavigate: (page: string) => void
}

const links = [
  { id: 'research', label: 'Research', icon: faMagnifyingGlass },
  { id: 'history', label: 'History', icon: faClockRotateLeft },
]

export default function Navbar({ page, onNavigate }: Props) {
  return (
    <header className="sticky top-0 z-10 border-b bg-white/80 dark:bg-gray-900/80 backdrop-blur-md">
      <div className="w-full px-6 flex h-14 items-center justify-between">
        <div className="flex items-center gap-6">
          <button onClick={() => onNavigate('research')} className="flex items-center gap-3">
            <img src="/favicon.svg" alt="Indorexia" className="h-8 w-8" />
            <span className="text-sm font-semibold text-gray-900 dark:text-white">Indorexia</span>
          </button>
          <nav className="flex gap-1">
            {links.map(l => (
              <button
                key={l.id}
                onClick={() => onNavigate(l.id)}
                className={`px-3.5 py-1.5 text-sm font-medium rounded-lg transition-all flex items-center gap-1.5 ${
                  page === l.id
                    ? 'bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              >
                <FontAwesomeIcon icon={l.icon} className="text-sm" />
                {l.label}
              </button>
            ))}
          </nav>
        </div>
        <span className="hidden sm:block text-xs text-gray-400 dark:text-gray-500">UMKM Research Tool</span>
      </div>
    </header>
  )
}
