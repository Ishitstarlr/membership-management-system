import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { getStoredUser, clearStoredUser, authApi } from '../api';

export default function Navbar() {
  const navigate = useNavigate();
  const user = getStoredUser();

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (e) {
      // Ignore network errors on logout, still clear token locally
    }
    clearStoredUser();
    navigate('/login');
  };

  if (!user) return null;

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          <span>ACM <span className="highlight">NITK</span></span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400 }}>| Membership Portal</span>
        </NavLink>

        <nav>
          <ul className="nav-links">
            <li>
              <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink to="/members" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                Members
              </NavLink>
            </li>
            <li>
              <NavLink to="/teams" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
                Teams
              </NavLink>
            </li>
          </ul>
        </nav>

        <div className="nav-user">
          <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{user.email}</span>
          <span className={`badge ${user.role === 'ADMIN' ? 'badge-role' : 'badge-active'}`}>
            {user.role}
          </span>
          <button onClick={handleLogout} className="btn btn-secondary btn-sm" title="Log out">
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
