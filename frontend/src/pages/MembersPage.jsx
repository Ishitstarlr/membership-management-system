import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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

export default function MembersPage() {
  const currentUser = getStoredUser();
  const isAdmin = currentUser?.role === 'ADMIN';

  const [members, setMembers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Available Teams for dropdown filter & assignment
  const [teams, setTeams] = useState([]);

  // Filter States
  const [search, setSearch] = useState('');
  const [selectedTeam, setSelectedTeam] = useState('');
  const [designation, setDesignation] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  // Modal State for Create / Edit
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    department: 'Computer Science & Engineering',
    year: 1,
    status: 'ACTIVE',
    bio: '',
    initial_team_id: '',
    initial_designation: 'Member',
  });
  const [modalError, setModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Fetch Teams for filter dropdown
  useEffect(() => {
    teamsApi.list()
      .then(data => setTeams(data))
      .catch(() => {});
  }, []);

  // Fetch Members
  const fetchMembers = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await membersApi.list({
        search,
        team_id: selectedTeam || undefined,
        designation: designation || undefined,
        department: selectedDept || undefined,
        year: selectedYear ? parseInt(selectedYear, 10) : undefined,
        status: selectedStatus || undefined,
        sort_by: sortBy,
        order: sortOrder,
        page,
        limit,
      });
      setMembers(data.members);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || 'Failed to fetch members');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [page, limit, selectedTeam, designation, selectedDept, selectedYear, selectedStatus, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchMembers();
  };

  const handleClearFilters = () => {
    setSearch('');
    setSelectedTeam('');
    setDesignation('');
    setSelectedDept('');
    setSelectedYear('');
    setSelectedStatus('');
    setSortBy('name');
    setSortOrder('asc');
    setPage(1);
  };

  const openCreateModal = () => {
    setEditingMember(null);
    setFormData({
      full_name: '',
      email: '',
      phone: '',
      department: 'Computer Science & Engineering',
      year: 1,
      status: 'ACTIVE',
      bio: '',
      initial_team_id: '',
      initial_designation: 'Member',
    });
    setModalError('');
    setIsModalOpen(true);
  };

  const openEditModal = (m) => {
    setEditingMember(m);
    setFormData({
      full_name: m.full_name,
      email: m.email,
      phone: m.phone || '',
      department: m.department,
      year: m.year,
      status: m.status,
      bio: m.bio || '',
      initial_team_id: '',
      initial_designation: '',
    });
    setModalError('');
    setIsModalOpen(true);
  };

  const handleDeleteMember = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete member "${name}"? This action cannot be undone.`)) {
      return;
    }
    try {
      await membersApi.delete(id);
      fetchMembers();
    } catch (err) {
      alert(err.message || 'Failed to delete member');
    }
  };

  const handleModalSubmit = async (e) => {
    e.preventDefault();
    setModalError('');
    setSubmitting(true);

    try {
      if (editingMember) {
        await membersApi.update(editingMember.id, {
          full_name: formData.full_name,
          email: formData.email,
          phone: formData.phone || null,
          department: formData.department,
          year: parseInt(formData.year, 10),
          status: formData.status,
          bio: formData.bio || null,
        });
      } else {
        const payload = {
          full_name: formData.full_name,
          email: formData.email,
          phone: formData.phone || null,
          department: formData.department,
          year: parseInt(formData.year, 10),
          status: formData.status,
          bio: formData.bio || null,
          teams: formData.initial_team_id ? [
            {
              team_id: parseInt(formData.initial_team_id, 10),
              designation: formData.initial_designation || 'Member',
            }
          ] : [],
        };
        await membersApi.create(payload);
      }
      setIsModalOpen(false);
      fetchMembers();
    } catch (err) {
      setModalError(err.message || 'Failed to save member details');
    } finally {
      setSubmitting(false);
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Members Directory</h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Showing {total} registered ACM NITK student members and alumni.
          </p>
        </div>
        {isAdmin && (
          <button onClick={openCreateModal} className="btn btn-primary">
            + Add New Member
          </button>
        )}
      </div>

      {/* Filter and Search Bar */}
      <form onSubmit={handleSearchSubmit} className="filter-bar">
        {/* Search Input */}
        <div className="filter-item search">
          <label className="form-label" htmlFor="member-search">Search Name / Email</label>
          <input
            id="member-search"
            type="text"
            className="form-input"
            placeholder="Type name or email & press Enter..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Team Filter */}
        <div className="filter-item">
          <label className="form-label" htmlFor="filter-team">Team / SIG</label>
          <select
            id="filter-team"
            className="form-select"
            value={selectedTeam}
            onChange={(e) => { setSelectedTeam(e.target.value); setPage(1); }}
          >
            <option value="">All Teams</option>
            {teams.map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>

        {/* Department Filter */}
        <div className="filter-item">
          <label className="form-label" htmlFor="filter-dept">Department</label>
          <select
            id="filter-dept"
            className="form-select"
            value={selectedDept}
            onChange={(e) => { setSelectedDept(e.target.value); setPage(1); }}
          >
            <option value="">All Departments</option>
            {DEPARTMENTS.map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </div>

        {/* Year Filter */}
        <div className="filter-item" style={{ maxWidth: '120px' }}>
          <label className="form-label" htmlFor="filter-year">Year</label>
          <select
            id="filter-year"
            className="form-select"
            value={selectedYear}
            onChange={(e) => { setSelectedYear(e.target.value); setPage(1); }}
          >
            <option value="">All Years</option>
            <option value="1">Year 1</option>
            <option value="2">Year 2</option>
            <option value="3">Year 3</option>
            <option value="4">Year 4</option>
          </select>
        </div>

        {/* Status Filter */}
        <div className="filter-item" style={{ maxWidth: '130px' }}>
          <label className="form-label" htmlFor="filter-status">Status</label>
          <select
            id="filter-status"
            className="form-select"
            value={selectedStatus}
            onChange={(e) => { setSelectedStatus(e.target.value); setPage(1); }}
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="INACTIVE">INACTIVE</option>
            <option value="ALUMNI">ALUMNI</option>
          </select>
        </div>

        {/* Sort Controls */}
        <div className="filter-item" style={{ maxWidth: '140px' }}>
          <label className="form-label" htmlFor="sort-by">Sort By</label>
          <select
            id="sort-by"
            className="form-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">Name</option>
            <option value="year">Year</option>
            <option value="date_joined">Date Joined</option>
          </select>
        </div>

        <div className="filter-item" style={{ maxWidth: '100px' }}>
          <label className="form-label" htmlFor="sort-order">Order</label>
          <select
            id="sort-order"
            className="form-select"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <option value="asc">Asc</option>
            <option value="desc">Desc</option>
          </select>
        </div>

        {/* Clear Filter Button */}
        <div style={{ display: 'flex', gap: '0.5rem', alignSelf: 'flex-end' }}>
          <button type="submit" className="btn btn-primary btn-sm" style={{ height: '38px' }}>
            Search
          </button>
          <button
            type="button"
            onClick={handleClearFilters}
            className="btn btn-secondary btn-sm"
            style={{ height: '38px' }}
          >
            Clear Filters
          </button>
        </div>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      {/* Members Table */}
      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div className="loading-spinner">Fetching member records...</div>
        ) : members.length === 0 ? (
          <div className="empty-state">
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>No members found</h3>
            <p>No results match your active search or filter criteria.</p>
            <button
              onClick={handleClearFilters}
              className="btn btn-secondary btn-sm"
              style={{ marginTop: '1rem' }}
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Department</th>
                  <th>Year</th>
                  <th>Status</th>
                  <th>Teams & Roles</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <Link to={`/members/${m.id}`} style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                        {m.full_name}
                      </Link>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{m.email}</div>
                    </td>
                    <td>{m.department}</td>
                    <td>Year {m.year}</td>
                    <td>
                      <span className={`badge badge-${m.status.toLowerCase()}`}>
                        {m.status}
                      </span>
                    </td>
                    <td>
                      {m.memberships.length === 0 ? (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No teams</span>
                      ) : (
                        m.memberships.map((ms) => (
                          <span key={ms.id} className="badge-chip">
                            <strong>{ms.team_name}</strong> ({ms.designation})
                          </span>
                        ))
                      )}
                    </td>
                    <td>{m.date_joined}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <Link to={`/members/${m.id}`} className="btn btn-secondary btn-sm">
                          View
                        </Link>
                        {isAdmin && (
                          <>
                            <button
                              onClick={() => openEditModal(m)}
                              className="btn btn-secondary btn-sm"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteMember(m.id, m.full_name)}
                              className="btn btn-danger btn-sm"
                            >
                              Delete
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Pagination Controls */}
      <div className="pagination">
        <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Showing Page {page} of {totalPages} ({total} total results)
        </span>
        <div className="pagination-controls">
          <button
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
            disabled={page <= 1}
            className="btn btn-secondary btn-sm"
          >
            ← Previous
          </button>
          <button
            onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
            disabled={page >= totalPages}
            className="btn btn-secondary btn-sm"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Create / Edit Modal (Admin Only) */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editingMember ? 'Edit Member Profile' : 'Add New Member'}</h3>
              <button className="modal-close" onClick={() => setIsModalOpen(false)}>×</button>
            </div>

            {modalError && <div className="alert alert-error">{modalError}</div>}

            <form onSubmit={handleModalSubmit}>
              <div className="form-group">
                <label className="form-label" htmlFor="m-name">Full Name *</label>
                <input
                  id="m-name"
                  type="text"
                  className="form-input"
                  required
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="m-email">Email Address *</label>
                  <input
                    id="m-email"
                    type="email"
                    className="form-input"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="m-phone">Phone Number</label>
                  <input
                    id="m-phone"
                    type="text"
                    className="form-input"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label" htmlFor="m-dept">Department *</label>
                  <select
                    id="m-dept"
                    className="form-select"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  >
                    {DEPARTMENTS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label" htmlFor="m-year">Year of Study *</label>
                  <select
                    id="m-year"
                    className="form-select"
                    value={formData.year}
                    onChange={(e) => setFormData({ ...formData, year: e.target.value })}
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
                <label className="form-label" htmlFor="m-status">Membership Status *</label>
                <select
                  id="m-status"
                  className="form-select"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="INACTIVE">INACTIVE</option>
                  <option value="ALUMNI">ALUMNI</option>
                </select>
              </div>

              {!editingMember && (
                <div className="card" style={{ background: '#f8fafc', padding: '1rem', marginTop: '1rem' }}>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.5rem' }}>Initial Team Assignment (Optional)</h4>
                  <div className="form-row">
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label" htmlFor="m-init-team">Assign to Team</label>
                      <select
                        id="m-init-team"
                        className="form-select"
                        value={formData.initial_team_id}
                        onChange={(e) => setFormData({ ...formData, initial_team_id: e.target.value })}
                      >
                        <option value="">-- None --</option>
                        {teams.map((t) => (
                          <option key={t.id} value={t.id}>{t.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                      <label className="form-label" htmlFor="m-init-desig">Designation</label>
                      <input
                        id="m-init-desig"
                        type="text"
                        className="form-input"
                        placeholder="e.g. Core Member, Lead"
                        value={formData.initial_designation}
                        onChange={(e) => setFormData({ ...formData, initial_designation: e.target.value })}
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="form-group" style={{ marginTop: '1rem' }}>
                <label className="form-label" htmlFor="m-bio">Bio / Notes</label>
                <textarea
                  id="m-bio"
                  rows="3"
                  className="form-textarea"
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                />
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? 'Saving...' : editingMember ? 'Update Member' : 'Create Member'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
