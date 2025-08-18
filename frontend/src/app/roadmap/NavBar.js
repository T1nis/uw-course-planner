import React, { useState } from 'react';
import Link from 'next/link';

const navItems = [
  { id: 'roadmap', label: 'Roadmap', href: '/roadmap' },
  { id: 'progress', label: 'Progress', href: '/progress' },
  // Add more items as needed
];

const Navigation = () => {
  const [activeLink, setActiveLink] = useState('roadmap');

  const handleNavClick = (itemId) => {
    setActiveLink(itemId);
  };

  const handleHomeClick = () => {
    window.location.href = '/';
  };

  return (
    <nav className="fixed top-0 w-full bg-[#1a1b2e]/95 backdrop-blur-sm border-b border-white/10 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo with Home Button */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleHomeClick}
              className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-colors duration-200"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Home</span>
            </button>
            <div className="h-6 w-px bg-white/20"></div>
            <h1 className="text-xl font-bold text-white">Course Planner</h1>
          </div>
          
          {/* Navigation Links */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map((item) => (
                <Link key={item.id} href={item.href}>
                  <span
                    onClick={() => handleNavClick(item.id)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 cursor-pointer ${
                      activeLink === item.id
                        ? 'bg-purple-500/20 text-purple-300 border border-purple-400/30'
                        : 'text-gray-300 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    {item.label}
                  </span>
                </Link>
              ))}
            </div>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden">
            <button className="text-gray-300 hover:text-white">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;