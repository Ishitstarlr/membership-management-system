import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return <div className="loading-spinner">Loading dashboard analytics...</div>;
  }

  if (error) {
    return (
      <div className="alert alert-error">
        {error}{' '}
        <button onClick={fetchStats} className="btn btn-secondary btn-sm" style={{ marginLeft: '1rem' }}>
          Retry
        </button>
      </div>
    );
  }

  if (!stats) return null;

  // Maximum counts for CSS progress bar scaling
  const maxDept = Math.max(...(stats.department_distribution.map(d => d.count)), 1);
  const maxYear = Math.max(...(stats.year_distribution.map(y => y.count)), 1);
  const maxTeam = Math.max(...(stats.team_distribution.map(t => t.count)), 1);

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Club Analytics Dashboard</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Real-time metrics derived dynamically from ACM NITK database records.
        </p>
      </div>

      {/* Top Stat Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Members</div>
          <div className="stat-value primary">{stats.total_members}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Members</div>
          <div className="stat-value success">{stats.active_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Inactive Members</div>
          <div className="stat-value warning">{stats.inactive_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Alumni</div>
          <div className="stat-value" style={{ color: '#6366f1' }}>{stats.alumni_count}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Teams / SIGs</div>
          <div className="stat-value">{stats.total_teams}</div>
        </div>
      </div>

      {/* Distribution Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Department Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1.25rem' }}>Department Breakdown</h2>
          {stats.department_distribution.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No department data available.</p>
          ) : (
            <div className="distribution-list">
              {stats.department_distribution.map((dept) => (
                <div key={dept.name} className="distribution-item">
                  <div className="distribution-header">
                    <span>{dept.name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{dept.count}</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${(dept.count / maxDept) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Year Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1.25rem' }}>Year of Study Breakdown</h2>
          {stats.year_distribution.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No year data available.</p>
          ) : (
            <div className="distribution-list">
              {stats.year_distribution.map((yr) => (
                <div key={yr.name} className="distribution-item">
                  <div className="distribution-header">
                    <span>{yr.name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{yr.count}</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${(yr.count / maxYear) * 100}%`, background: '#059669' }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Team Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1.25rem' }}>Team / SIG Membership</h2>
          {stats.team_distribution.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No team memberships assigned yet.</p>
          ) : (
            <div className="distribution-list">
              {stats.team_distribution.map((t) => (
                <div key={t.name} className="distribution-item">
                  <div className="distribution-header">
                    <span>{t.name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{t.count} members</span>
                  </div>
                  <div className="progress-bar-bg">
                    <div
                      className="progress-bar-fill"
                      style={{ width: `${(t.count / maxTeam) * 100}%`, background: '#8b5cf6' }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Recently Added Members Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recently Added Members</h2>
          <Link to="/members" className="btn btn-secondary btn-sm">
            View All Members →
          </Link>
        </div>

        {stats.recent_members.length === 0 ? (
          <div className="empty-state">No recent members recorded.</div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Member Name</th>
                  <th>Department</th>
                  <th>Year</th>
                  <th>Status</th>
                  <th>Date Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_members.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <strong>{m.full_name}</strong>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.email}</div>
                    </td>
                    <td>{m.department}</td>
                    <td>Year {m.year}</td>
                    <td>
                      <span className={`badge badge-${m.status.toLowerCase()}`}>
                        {m.status}
                      </span>
                    </td>
                    <td>{m.date_joined}</td>
                    <td>
                      <Link to={`/members/${m.id}`} className="btn btn-secondary btn-sm">
                        View Profile
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
