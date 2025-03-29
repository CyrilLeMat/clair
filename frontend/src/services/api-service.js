// api.js - API Service for Clair UI

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Base API request function with error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      // Try to parse error message from response
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { detail: `HTTP error ${response.status}` };
      }
      
      const error = new Error(errorData.detail || 'API request failed');
      error.status = response.status;
      error.data = errorData;
      throw error;
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * API service object with endpoint methods
 */
const api = {
  // Sources
  getSources: () => 
    apiRequest('/sources'),
  
  addSource: (sourceType, credentials) => 
    apiRequest('/sources', {
      method: 'POST',
      body: JSON.stringify({
        source_type: sourceType,
        credentials: credentials
      }),
    }),
  
  deleteSource: (sourceId) => 
    apiRequest(`/sources/${sourceId}`, {
      method: 'DELETE',
    }),
  
  // Issues
  getIssues: (filters = {}) => {
    const queryParams = new URLSearchParams();
    
    if (filters.sourceType) queryParams.append('source_type', filters.sourceType);
    if (filters.issueType) queryParams.append('issue_type', filters.issueType);
    if (filters.severity) queryParams.append('severity', filters.severity);
    if (filters.limit) queryParams.append('limit', filters.limit);
    if (filters.offset) queryParams.append('offset', filters.offset);
    
    const queryString = queryParams.toString();
    return apiRequest(`/issues${queryString ? `?${queryString}` : ''}`);
  },
  
  getIssueDetails: (issueId) => 
    apiRequest(`/issues/${issueId}`),
  
  // Audits
  startAudit: (sourceIds = []) => 
    apiRequest('/audits', {
      method: 'POST',
      body: JSON.stringify({ source_ids: sourceIds }),
    }),
  
  getAudits: (limit = 10) => 
    apiRequest(`/audits?limit=${limit}`),
  
  getAuditDetails: (auditId) => 
    apiRequest(`/audits/${auditId}`),
  
  // Dashboard stats
  getOverviewStats: () => 
    apiRequest('/stats/overview'),
};

export default api;
