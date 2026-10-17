import React from 'react';
import { Navigate } from 'react-router-dom';
import { getStoredUser } from '../api';

export default function ProtectedRoute({ children }) {
  const user = getStoredUser();

  if (!user || !user.token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
