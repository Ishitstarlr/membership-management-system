// API client with token management and error handling

const API_BASE = '/api';

export function getStoredUser() {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const email = localStorage.getItem('email');
  const userId = localStorage.getItem('userId');
  if (!token) return null;
  return { token, role, email, userId: parseInt(userId, 10) };
}

export function setStoredUser(data) {
  localStorage.setItem('token', data.access_token);
  localStorage.setItem('role', data.role);
  localStorage.setItem('email', data.email);
  localStorage.setItem('userId', data.user_id);
}

export function clearStoredUser() {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('email');
  localStorage.removeItem('userId');
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle unauthorized (401)
  if (response.status === 401 && !endpoint.includes('/auth/login')) {
    clearStoredUser();
    window.location.href = '/login';
    throw new Error('Session expired. Please log in again.');
  }

  const contentType = response.headers.get('content-type');
  const data = contentType && contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    let errorMessage = 'An error occurred';
    if (typeof data === 'object' && data !== null) {
      if (Array.isArray(data.detail)) {
        errorMessage = data.detail.map(d => `${d.loc ? d.loc.join('.') : ''}: ${d.msg}`).join(', ');
      } else if (data.detail) {
        errorMessage = data.detail;
      } else if (data.message) {
        errorMessage = data.message;
      }
    } else if (typeof data === 'string') {
      errorMessage = data;
    }
    const error = new Error(errorMessage);
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

// Auth API
export const authApi = {
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (email, password) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  getMe: () => request('/auth/me'),
  logout: () =>
    request('/auth/logout', {
      method: 'POST',
    }),
};

// Members API
export const membersApi = {
  list: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    return request(`/members?${query.toString()}`);
  },
  get: (id) => request(`/members/${id}`),
  create: (data) =>
    request('/members', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    request(`/members/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id) =>
    request(`/members/${id}`, {
      method: 'DELETE',
    }),
  assignTeam: (memberId, teamId, designation) =>
    request(`/members/${memberId}/teams`, {
      method: 'POST',
      body: JSON.stringify({ team_id: teamId, designation }),
    }),
  updateTeamDesignation: (memberId, teamId, designation) =>
    request(`/members/${memberId}/teams/${teamId}`, {
      method: 'PUT',
      body: JSON.stringify({ designation }),
    }),
  removeFromTeam: (memberId, teamId) =>
    request(`/members/${memberId}/teams/${teamId}`, {
      method: 'DELETE',
    }),
};

// Teams API
export const teamsApi = {
  list: () => request('/teams'),
  get: (id) => request(`/teams/${id}`),
  create: (data) =>
    request('/teams', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  update: (id, data) =>
    request(`/teams/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  delete: (id) =>
    request(`/teams/${id}`, {
      method: 'DELETE',
    }),
};

// Dashboard API
export const dashboardApi = {
  getStats: () => request('/dashboard/stats'),
};
