import ContactPanel from "../ContactPanel/ContactPanel";
import LinePanel from "../LinePanel/LinePanel";
import MicControls from "../MicControls/MicControls";
import Soundboard from "../Soundboard/Soundboard";
import TTSPanel from "../TTSPanel/TTSPanel";

export default function Dashboard() {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-surface text-gray-100">
      {/* Top bar: contact management */}
      <header className="flex-shrink-0 border-b border-gray-700 bg-surface-light">
        <div className="flex items-center gap-3 px-4 py-2">
          <span className="text-sm font-bold text-accent-blue tracking-wider uppercase">
            Spam Baiter
          </span>
          <div className="w-px h-4 bg-gray-700" />
          <ContactPanel />
        </div>
      </header>

      {/* Main 3-column body */}
      <main className="flex-1 flex min-h-0">
        {/* Left: Lines */}
        <aside className="w-64 flex-shrink-0 border-r border-gray-700 flex flex-col overflow-hidden">
          <LinePanel />
        </aside>

        {/* Center: TTS */}
        <section className="flex-1 border-r border-gray-700 flex flex-col overflow-hidden min-w-0">
          <TTSPanel />
        </section>

        {/* Right: Soundboard */}
        <aside className="w-72 flex-shrink-0 flex flex-col overflow-hidden">
          <Soundboard />
        </aside>
      </main>

      {/* Bottom bar: mic controls */}
      <footer className="flex-shrink-0">
        <MicControls />
      </footer>
    </div>
  );
}
