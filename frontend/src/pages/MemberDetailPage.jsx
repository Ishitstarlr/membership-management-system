import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { membersApi, teamsApi, getStoredUser } from '../api';

const DEPARTMENTS = [
  'Computer Science & Engineering',
  'Information Technology',
  'Electronics & Communication',
  'Electrical & Electronics',
  'Mechanical Engineering',
  'Civil Engineering',
  'Chemical Engineering',
];

export default function MemberDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const currentUser = getStoredUser();
  const isAdmin = currentUser?.role === 'ADMIN';

  const [member, setMember] = useState(null);
  const [allTeams, setAllTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Editing profile state
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    department: '',
    year: 1,
    status: 'ACTIVE',
    bio: '',
  });

  // Assigning to new team state
  const [isAssigningTeam, setIsAssigningTeam] = useState(false);
  const [assignForm, setAssignForm] = useState({
    team_id: '',
    designation: 'Member',
  });

  // Editing existing team designation
  const [editingTeamId, setEditingTeamId] = useState(null);
  const [newDesignation, setNewDesignation] = useState('');

  const fetchMemberAndTeams = async () => {
    setLoading(true);
    setError('');
    try {
      const [m, tList] = await Promise.all([
        membersApi.get(id),
        teamsApi.list(),
      ]);
      setMember(m);
      setAllTeams(tList);
      setProfileForm({
        full_name: m.full_name,
        email: m.email,
        phone: m.phone || '',
        department: m.department,
        year: m.year,
        status: m.status,
        bio: m.bio || '',
      });
    } catch (err) {
      setError(err.message || 'Failed to fetch member details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMemberAndTeams();
  }, [id]);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      const updated = await membersApi.update(id, {
        full_name: profileForm.full_name,
        email: profileForm.email,
        phone: profileForm.phone || null,
        department: profileForm.department,
        year: parseInt(profileForm.year, 10),
        status: profileForm.status,
        bio: profileForm.bio || null,
      });
      setMember(updated);
      setIsEditingProfile(false);
      setSuccess('Profile updated successfully.');
    } catch (err) {
      setError(err.message || 'Failed to update profile');
    }
  };

  const handleAssignTeam = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!assignForm.team_id) {
      setError('Please select a team.');
      return;
    }

    try {
      await membersApi.assignTeam(
        id,
        parseInt(assignForm.team_id, 10),
        assignForm.designation
      );
      setSuccess('Team assigned successfully.');
      setIsAssigningTeam(false);
      setAssignForm({ team_id: '', designation: 'Member' });
      fetchMemberAndTeams();
    } catch (err) {
      setError(err.message || 'Failed to assign team');
    }
  };

  const handleUpdateDesignation = async (teamId) => {
    setError('');
    setSuccess('');
    if (!newDesignation.trim()) return;

    try {
      await membersApi.updateTeamDesignation(id, teamId, newDesignation.trim());
      setSuccess('Designation updated.');
      setEditingTeamId(null);
      setNewDesignation('');
      fetchMemberAndTeams();
    } catch (err) {
      setError(err.message || 'Failed to update designation');
    }
  };

  const handleRemoveFromTeam = async (teamId, teamName) => {
    if (!window.confirm(`Remove ${member.full_name} from ${teamName}?`)) {
      return;
    }
    setError('');
    setSuccess('');
    try {
      await membersApi.removeFromTeam(id, teamId);
      setSuccess(`Removed from ${teamName}.`);
      fetchMemberAndTeams();
    } catch (err) {
      setError(err.message || 'Failed to remove from team');
    }
  };

  const handleDeleteMember = async () => {
    if (!window.confirm(`Delete member ${member.full_name} permanently?`)) {
      return;
    }
    try {
      await membersApi.delete(id);
      navigate('/members');
    } catch (err) {
      setError(err.message || 'Failed to delete member');
    }
  };

  if (loading) {
    return <div className="loading-spinner">Loading member profile...</div>;
  }

  if (error && !member) {
    return (
      <div className="alert alert-error">
        {error}{' '}
        <Link to="/members" className="btn btn-secondary btn-sm" style={{ marginLeft: '1rem' }}>
          Back to Directory
        </Link>
      </div>
    );
  }

  if (!member) return null;

  // Find teams the member is NOT currently assigned to
  const assignedTeamIds = new Set(member.memberships.map((ms) => ms.team_id));
  const availableTeamsToAssign = allTeams.filter((t) => !assignedTeamIds.has(t.id));

  return (
    <div>
      <div style={{ marginBottom: '1.25rem' }}>
        <Link to="/members" style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          ← Back to Members Directory
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Profile Card */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Profile Information</h2>
            {isAdmin && !isEditingProfile && (
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setIsEditingProfile(true)}
                  className="btn btn-secondary btn-sm"
                >
                  Edit Profile
                </button>
                <button
                  onClick={handleDeleteMember}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            )}
          </div>

          {!isEditingProfile ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <div
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: 'var(--primary-light)',
                    color: 'var(--primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.5rem',
                    fontWeight: 700,
                  }}
                >
                  {member.full_name.charAt(0)}
                </div>
                <div>
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>{member.full_name}</h3>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.25rem' }}>
                    <span className={`badge badge-${member.status.toLowerCase()}`}>
                      {member.status}
                    </span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                      Joined on {member.date_joined}
                    </span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.95rem' }}>
                <div>
                  <strong style={{ color: 'var(--text-muted)', display: 'inline-block', width: '120px' }}>Email:</strong>
                  <span>{member.email}</span>
                </div>
                <div>
                  <strong style={{ color: 'var(--text-muted)', display: 'inline-block', width: '120px' }}>Phone:</strong>
                  <span>{member.phone || 'Not provided'}</span>
                </div>
                <div>
                  <strong style={{ color: 'var(--text-muted)', display: 'inline-block', width: '120px' }}>Department:</strong>
                  <span>{member.department}</span>
                </div>
                <div>
                  <strong style={{ color: 'var(--text-muted)', display: 'inline-block', width: '120px' }}>Year of Study:</strong>
                  <span>Year {member.year}</span>
                </div>
                {member.bio && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <strong style={{ color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>Bio / Notes:</strong>
                    <p style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
                      {member.bio}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <form onSubmit={handleProfileUpdate}>
              <div className="form-group">
                <label className="form-label" htmlFor="edit-name">Full Name</label>
                <input
                  id="edit-name"
                  type="text"
                  className="form-input"
                  required
                  value={profileForm.full_name}
                  onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="edit-email">Email Address</label>
                <input
                  id="edit-email"
                  type="email"
                  className="form-input"
                  required
                  value={profileForm.email}
                  onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="edit-phone">Phone Number</label>
                <input
                  id="edit-phone"
                  type="text"
                  className="form-input"
                  value={profileForm.phone}
                  onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="edit-dept">Department</label>
                  <select
                    id="edit-dept"
                    className="form-select"
                    value={profileForm.department}
                    onChange={(e) => setProfileForm({ ...profileForm, department: e.target.value })}
                  >
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label" htmlFor="edit-year">Year</label>
                  <select
                    id="edit-year"
                    className="form-select"
                    value={profileForm.year}
                    onChange={(e) => setProfileForm({ ...profileForm, year: e.target.value })}
                  >
                    <option value="1">Year 1</option>
                    <option value="2">Year 2</option>
                    <option value="3">Year 3</option>
                    <option value="4">Year 4</option>
                    <option value="5">Year 5</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="edit-status">Status</label>
                <select
                  id="edit-status"
                  className="form-select"
                  value={profileForm.status}
                  onChange={(e) => setProfileForm({ ...profileForm, status: e.target.value })}
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                  <option value="ALUMNI">ALUMNI</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="edit-bio">Bio / Notes</label>
                <textarea
                  id="edit-bio"
                  rows="3"
                  className="form-textarea"
                  value={profileForm.bio}
                  onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsEditingProfile(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary btn-sm">
                  Save Changes
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Assigned Teams Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Assigned Teams & Roles</h2>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Multiple teams per member with independent designations.
              </span>
            </div>
            {isAdmin && !isAssigningTeam && availableTeamsToAssign.length > 0 && (
              <button
                onClick={() => setIsAssigningTeam(true)}
                className="btn btn-primary btn-sm"
              >
                + Assign Team
              </button>
            )}
          </div>

          {/* Form to assign a new team */}
          {isAssigningTeam && (
            <form onSubmit={handleAssignTeam} style={{ background: '#f8fafc', padding: '1rem', borderRadius: 'var(--radius)', border: '1px solid var(--border)', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>Assign New Team</h3>
              <div className="form-group">
                <label className="form-label" htmlFor="new-team-select">Select Team</label>
                <select
                  id="new-team-select"
                  className="form-select"
                  required
                  value={assignForm.team_id}
                  onChange={(e) => setAssignForm({ ...assignForm, team_id: e.target.value })}
                >
                  <option value="">-- Choose Team --</option>
                  {availableTeamsToAssign.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="new-team-desig">Designation in this Team</label>
                <input
                  id="new-team-desig"
                  type="text"
                  className="form-input"
                  required
                  placeholder="e.g. Lead, Core, Executive, Mentee"
                  value={assignForm.designation}
                  onChange={(e) => setAssignForm({ ...assignForm, designation: e.target.value })}
                />
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsAssigningTeam(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary btn-sm">
                  Save Assignment
                </button>
              </div>
            </form>
          )}

          {/* Teams Table / List */}
          {member.memberships.length === 0 ? (
            <div className="empty-state">
              <p>This member is not assigned to any teams or SIGs.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Team Name</th>
                    <th>Designation</th>
                    <th>Assigned Since</th>
                    {isAdmin && <th>Actions</th>}
                  </tr>
                </thead>
                <tbody>
                  {member.memberships.map((ms) => (
                    <tr key={ms.id}>
                      <td>
                        <strong>{ms.team_name}</strong>
                      </td>
                      <td>
                        {editingTeamId === ms.team_id ? (
                          <div style={{ display: 'flex', gap: '0.25rem' }}>
                            <input
                              type="text"
                              className="form-input"
                              style={{ padding: '0.2rem 0.5rem', fontSize: '0.85rem' }}
                              value={newDesignation}
                              onChange={(e) => setNewDesignation(e.target.value)}
                            />
                            <button
                              onClick={() => handleUpdateDesignation(ms.team_id)}
                              className="btn btn-primary btn-sm"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setEditingTeamId(null)}
                              className="btn btn-secondary btn-sm"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <span className="badge-chip" style={{ fontWeight: 600 }}>
                            {ms.designation}
                          </span>
                        )}
                      </td>
                      <td>{ms.joined_at}</td>
                      {isAdmin && (
                        <td>
                          {editingTeamId !== ms.team_id && (
                            <div style={{ display: 'flex', gap: '0.35rem' }}>
                              <button
                                onClick={() => {
                                  setEditingTeamId(ms.team_id);
                                  setNewDesignation(ms.designation);
                                }}
                                className="btn btn-secondary btn-sm"
                              >
                                Edit Role
                              </button>
                              <button
                                onClick={() => handleRemoveFromTeam(ms.team_id, ms.team_name)}
                                className="btn btn-danger btn-sm"
                              >
                                Remove
                              </button>
                            </div>
                          )}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
