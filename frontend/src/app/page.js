export default function Home() {
  return (
    <div>
      {/* Simple navigation for home page */}
      <nav className="fixed top-0 w-full bg-[#171923]/95 backdrop-blur-sm border-b border-white/10 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-white">Course Planner</h1>
            </div>
            <div>
              <a
                href="/roadmap"
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-colors duration-200"
              >
                Roadmap
              </a>
            </div>
          </div>
        </div>
      </nav>

      <main className="min-h-screen bg-gradient-to-br from-[#171923] via-[#22223c] to-[#29304d] flex flex-col items-center justify-center px-4 pt-16">
        {/* Hero */}
        <section className="text-center mb-16">
          <h1 className="text-5xl sm:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-green-300 to-blue-500 mb-4 drop-shadow-lg">
            Plan Your Path to Graduation
          </h1>
          <p className="text-lg sm:text-xl text-gray-300 max-w-xl mx-auto mb-8">
            Build your custom roadmap, track requirements, and never miss a class—designed for modern college students.
          </p>
          <a
            href="/roadmap"
            className="inline-block px-8 py-3 bg-blue-600/80 hover:bg-blue-500/90 transition rounded-2xl text-white font-semibold text-lg shadow-lg backdrop-blur"
          >
            Get Started
          </a>
        </section>

        {/* Features */}
        <section className="flex flex-col sm:flex-row gap-8 justify-center">
          <FeatureCard
            icon="🎯"
            title="Smart Roadmap"
            desc="Visualize each semester with prerequisites, electives, and gen eds automatically organized."
          />
          <FeatureCard
            icon="📈"
            title="Progress Tracker"
            desc="See your graduation progress, required credits, and completed classes in one place."
          />
          <FeatureCard
            icon="🔎"
            title="Requirement Checker"
            desc="Never miss a course—instantly see what you need for your major or minor."
          />
        </section>
      </main>
    </div>
  );
}

// Keep your existing FeatureCard function exactly the same
function FeatureCard({ icon, title, desc }) {
  return (
    <div className="flex-1 bg-white/10 border border-white/20 rounded-2xl shadow-xl px-6 py-8 min-w-[250px] max-w-xs transition hover:scale-105 hover:shadow-2xl backdrop-blur-lg">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-gray-300">{desc}</p>
    </div>
  );
}