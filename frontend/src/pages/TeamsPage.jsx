import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { teamsApi, membersApi, getStoredUser } from '../api';

export default function TeamsPage() {
  const currentUser = getStoredUser();
  const isAdmin = currentUser?.role === 'ADMIN';

  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Roster View Modal / Detail
  const [selectedTeamDetail, setSelectedTeamDetail] = useState(null);
  const [rosterLoading, setRosterLoading] = useState(false);

  // All members list for team lead selection dropdown
  const [allMembers, setAllMembers] = useState([]);

  // Create / Edit Team Modal
  const [isTeamModalOpen, setIsTeamModalOpen] = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  const [teamForm, setTeamForm] = useState({
    name: '',
    description: '',
    team_lead_id: '',
  });
  const [teamModalError, setTeamModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchTeams = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await teamsApi.list();
      setTeams(data);
    } catch (err) {
      setError(err.message || 'Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
    // Load members for lead assignment
    membersApi.list({ limit: 100 })
      .then((data) => setAllMembers(data.members))
      .catch(() => {});
  }, []);

  const openViewRoster = async (teamId) => {
    setRosterLoading(true);
    try {
      const detail = await teamsApi.get(teamId);
      setSelectedTeamDetail(detail);
    } catch (err) {
      alert(err.message || 'Failed to load team roster');
    } finally {
      setRosterLoading(false);
    }
  };

  const openCreateTeamModal = () => {
    setEditingTeam(null);
    setTeamForm({ name: '', description: '', team_lead_id: '' });
    setTeamModalError('');
    setIsTeamModalOpen(true);
  };

  const openEditTeamModal = (team) => {
    setEditingTeam(team);
    setTeamForm({
      name: team.name,
      description: team.description || '',
      team_lead_id: team.team_lead_id ? team.team_lead_id.toString() : '',
    });
    setTeamModalError('');
    setIsTeamModalOpen(true);
  };

  const handleDeleteTeam = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete team "${name}"? This will remove all associated member assignments.`)) {
      return;
    }
    setError('');
    setSuccess('');
    try {
      await teamsApi.delete(id);
      setSuccess(`Team "${name}" deleted successfully.`);
      fetchTeams();
      if (selectedTeamDetail && selectedTeamDetail.id === id) {
        setSelectedTeamDetail(null);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete team');
    }
  };

  const handleTeamFormSubmit = async (e) => {
    e.preventDefault();
    setTeamModalError('');
    setSubmitting(true);

    const payload = {
      name: teamForm.name.trim(),
      description: teamForm.description.trim() || null,
      team_lead_id: teamForm.team_lead_id ? parseInt(teamForm.team_lead_id, 10) : null,
    };

    try {
      if (editingTeam) {
        await teamsApi.update(editingTeam.id, payload);
        setSuccess(`Team "${payload.name}" updated successfully.`);
      } else {
        await teamsApi.create(payload);
        setSuccess(`Team "${payload.name}" created successfully.`);
      }
      setIsTeamModalOpen(false);
      fetchTeams();
    } catch (err) {
      setTeamModalError(err.message || 'Failed to save team');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Teams & Special Interest Groups (SIGs)</h1>
          <p style={{ color: 'var(--text-muted)' }}>
            ACM NITK specialized working groups, team leads, and member rosters.
          </p>
        </div>
        {isAdmin && (
          <button onClick={openCreateTeamModal} className="btn btn-primary">
            + Create New Team
          </button>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {loading ? (
        <div className="loading-spinner">Loading teams...</div>
      ) : teams.length === 0 ? (
        <div className="card empty-state">
          <h3>No teams created yet</h3>
          {isAdmin && (
            <button onClick={openCreateTeamModal} className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }}>
              Create First Team
            </button>
          )}
        </div>
      ) : (
        <div className="teams-grid">
          {teams.map((t) => (
            <div key={t.id} className="team-card">
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)' }}>{t.name}</h3>
                  <span className="badge badge-active" style={{ fontSize: '0.75rem' }}>
                    {t.member_count} {t.member_count === 1 ? 'member' : 'members'}
                  </span>
                </div>

                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem', minHeight: '40px' }}>
                  {t.description || 'No description provided.'}
                </p>

                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)', marginBottom: '1rem', fontSize: '0.85rem' }}>
                  <div style={{ color: 'var(--text-muted)', fontWeight: 500 }}>Team Lead</div>
                  <div style={{ fontWeight: 600, marginTop: '0.2rem' }}>
                    {t.team_lead_name ? (
                      <Link to={`/members/${t.team_lead_id}`}>{t.team_lead_name}</Link>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Unassigned</span>
                    )}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: '1rem', marginTop: '0.5rem' }}>
                <button
                  onClick={() => openViewRoster(t.id)}
                  className="btn btn-secondary btn-sm"
                >
                  View Roster ({t.member_count})
                </button>
                {isAdmin && (
                  <div style={{ display: 'flex', gap: '0.4rem' }}>
                    <button
                      onClick={() => openEditTeamModal(t)}
                      className="btn btn-secondary btn-sm"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDeleteTeam(t.id, t.name)}
                      className="btn btn-danger btn-sm"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Roster Modal */}
      {selectedTeamDetail && (
        <div className="modal-overlay" onClick={() => setSelectedTeamDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '700px' }}>
            <div className="modal-header">
              <div>
                <h3 className="modal-title">{selectedTeamDetail.name} — Member Roster</h3>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                  Lead: {selectedTeamDetail.team_lead_name || 'Unassigned'} | Total: {selectedTeamDetail.member_count} members
                </span>
              </div>
              <button className="modal-close" onClick={() => setSelectedTeamDetail(null)}>×</button>
            </div>

            {selectedTeamDetail.roster.length === 0 ? (
              <div className="empty-state">
                <p>No members currently assigned to this team.</p>
              </div>
            ) : (
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Member Name</th>
                      <th>Designation in Team</th>
                      <th>Status</th>
                      <th>Profile</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedTeamDetail.roster.map((m) => (
                      <tr key={m.member_id}>
                        <td>
                          <strong>{m.full_name}</strong>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.email}</div>
                        </td>
                        <td>
                          <span className="badge-chip" style={{ fontWeight: 600 }}>
                            {m.designation}
                          </span>
                        </td>
                        <td>
                          <span className={`badge badge-${m.status.toLowerCase()}`}>
                            {m.status}
                          </span>
                        </td>
                        <td>
                          <Link
                            to={`/members/${m.member_id}`}
                            className="btn btn-secondary btn-sm"
                            onClick={() => setSelectedTeamDetail(null)}
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setSelectedTeamDetail(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create / Edit Team Modal (Admin Only) */}
      {isTeamModalOpen && (
        <div className="modal-overlay" onClick={() => setIsTeamModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editingTeam ? 'Edit Team Details' : 'Create New Team'}</h3>
              <button className="modal-close" onClick={() => setIsTeamModalOpen(false)}>×</button>
            </div>

            {teamModalError && <div className="alert alert-error">{teamModalError}</div>}

            <form onSubmit={handleTeamFormSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="team-name">Team Name *</label>
                <input
                  id="team-name"
                  type="text"
                  className="form-input"
                  required
                  placeholder="e.g. Web Development, AI/ML SIG"
                  value={teamForm.name}
                  onChange={(e) => setTeamForm({ ...teamForm, name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="team-desc">Description</label>
                <textarea
                  id="team-desc"
                  rows="3"
                  className="form-textarea"
                  placeholder="Brief description of SIG mission and activities"
                  value={teamForm.description}
                  onChange={(e) => setTeamForm({ ...teamForm, description: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="team-lead">Assign Team Lead (Optional)</label>
                <select
                  id="team-lead"
                  className="form-select"
                  value={teamForm.team_lead_id}
                  onChange={(e) => setTeamForm({ ...teamForm, team_lead_id: e.target.value })}
                >
                  <option value="">-- None / Unassigned --</option>
                  {allMembers.map((m) => (
                    <option key={m.id} value={m.id}>{m.full_name} ({m.department})</option>
                  ))}
                </select>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsTeamModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Saving...' : editingTeam ? 'Update Team' : 'Create Team'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
