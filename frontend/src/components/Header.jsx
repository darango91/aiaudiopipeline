import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex items-center">
          <h1 className="text-xl font-bold">AI Audio Assistant</h1>
        </div>
        <nav>
          <ul className="flex space-x-6">
            <li>
              <Link to="/" className="hover:text-blue-200">Dashboard</Link>
            </li>
            <li>
              <Link to="/keywords" className="hover:text-blue-200">Keywords</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

export default Header;
