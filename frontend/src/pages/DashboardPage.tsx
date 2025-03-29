import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertCircle, FileText, RefreshCw, Settings, Database, Zap, Clock, Search } from 'lucide-react';

const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Sample data
  const issuesByType = [
    { name: 'Contradictions', count: 12, color: '#FF6B6B' },
    { name: 'Outdated', count: 8, color: '#FFD166' },
    { name: 'Ambiguous', count: 15, color: '#06D6A0' },
    { name: 'Misalignment', count: 5, color: '#118AB2' },
  ];
  
  const recentIssues = [
    { id: 1, type: 'Contradiction', source: 'Onboarding.md', target: 'HR-Policy.md', description: 'Different probation periods specified' },
    { id: 2, type: 'Outdated', source: 'API-Documentation.md', description: 'References deprecated endpoints', lastUpdated: '342 days ago' },
    { id: 3, type: 'Ambiguous', source: 'Release-Process.md', description: 'Unclear approval requirements', severity: 'High' },
    { id: 4, type: 'Misalignment', source: 'Project-Guidelines.md', description: 'Document says daily standups, Slack shows weekly', evidence: 'Slack analysis' },
  ];
  
  const sources = [
    { id: 1, name: 'Notion', status: 'Connected', docsCount: 156, lastScan: '2 hours ago' },
    { id: 2, name: 'Confluence', status: 'Connected', docsCount: 243, lastScan: '1 day ago' },
    { id: 3, name: 'Slack', status: 'Not connected', docsCount: 0, lastScan: 'Never' },
  ];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold text-indigo-700">✨ Clair</h1>
          <p className="text-xs text-gray-500">Documentation Auditor</p>
        </div>
        <nav className="p-4">
          <ul>
            <li className={`mb-2 p-2 rounded ${activeTab === 'dashboard' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`} 
                onClick={() => setActiveTab('dashboard')}>
              <a href="#" className="flex items-center">
                <Zap size={16} className="mr-2" />
                Dashboard
              </a>
            </li>
            <li className={`mb-2 p-2 rounded ${activeTab === 'issues' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`}
                onClick={() => setActiveTab('issues')}>
              <a href="#" className="flex items-center">
                <AlertCircle size={16} className="mr-2" />
                Issues
              </a>
            </li>
            <li className={`mb-2 p-2 rounded ${activeTab === 'sources' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`}
                onClick={() => setActiveTab('sources')}>
              <a href="#" className="flex items-center">
                <Database size={16} className="mr-2" />
                Sources
              </a>
            </li>
            <li className={`mb-2 p-2 rounded ${activeTab === 'settings' ? 'bg-indigo-100 text-indigo-700' : 'text-gray-700 hover:bg-gray-100'}`}
                onClick={() => setActiveTab('settings')}>
              <a href="#" className="flex items-center">
                <Settings size={16} className="mr-2" />
                Settings
              </a>
            </li>
          </ul>
        </nav>
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-y-auto">
        <header className="bg-white shadow">
          <div className="flex justify-between items-center p-4">
            <h2 className="text-xl font-semibold text-gray-800">Dashboard</h2>
            <div className="flex">
              <button className="mr-2 px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                <Search size={16} className="inline mr-1" /> 
                Search Docs
              </button>
              <button className="px-4 py-2 bg-indigo-600 rounded-md text-sm font-medium text-white hover:bg-indigo-700">
                <RefreshCw size={16} className="inline mr-1" /> 
                Run Audit
              </button>
            </div>
          </div>
        </header>
        
        <main className="p-6">
          {/* Stats overview */}
          <div className="grid grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className="rounded-full bg-red-100 p-3 mr-4">
                  <AlertCircle size={20} className="text-red-500" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Total Issues</p>
                  <p className="text-2xl font-bold text-gray-800">40</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className="rounded-full bg-yellow-100 p-3 mr-4">
                  <FileText size={20} className="text-yellow-600" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Docs Scanned</p>
                  <p className="text-2xl font-bold text-gray-800">399</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className="rounded-full bg-blue-100 p-3 mr-4">
                  <Database size={20} className="text-blue-500" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Connected Sources</p>
                  <p className="text-2xl font-bold text-gray-800">2/3</p>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center">
                <div className="rounded-full bg-green-100 p-3 mr-4">
                  <Clock size={20} className="text-green-500" />
                </div>
                <div>
                  <p className="text-sm text-gray-500">Last Audit</p>
                  <p className="text-2xl font-bold text-gray-800">2h ago</p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Issues by type chart */}
          <div className="grid grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Issues by Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={issuesByType}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            {/* Recent issues */}
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Recent Issues</h3>
              <div className="overflow-y-auto max-h-80">
                {recentIssues.map(issue => (
                  <div key={issue.id} className="mb-4 border-b pb-3">
                    <div className="flex justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-medium 
                        ${issue.type === 'Contradiction' ? 'bg-red-100 text-red-800' : 
                          issue.type === 'Outdated' ? 'bg-yellow-100 text-yellow-800' :
                          issue.type === 'Ambiguous' ? 'bg-green-100 text-green-800' : 
                          'bg-blue-100 text-blue-800'}`}>
                        {issue.type}
                      </span>
                      <span className="text-xs text-gray-500">
                        {issue.lastUpdated ? `Updated: ${issue.lastUpdated}` : ''}
                      </span>
                    </div>
                    <h4 className="text-sm font-medium mt-2">
                      {issue.source} 
                      {issue.target && <span> → {issue.target}</span>}
                    </h4>
                    <p className="text-sm text-gray-600 mt-1">{issue.description}</p>
                  </div>
                ))}
              </div>
              <button className="w-full mt-2 text-sm text-indigo-600 hover:text-indigo-800">
                View all issues →
              </button>
            </div>
          </div>
          
          {/* Connected sources */}
          <div className="mt-6">
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Connected Sources</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Source</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Documents</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Last Scan</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sources.map(source => (
                      <tr key={source.id} className="border-b">
                        <td className="py-3 px-4">{source.name}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium 
                            ${source.status === 'Connected' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                            {source.status}
                          </span>
                        </td>
                        <td className="py-3 px-4">{source.docsCount}</td>
                        <td className="py-3 px-4">{source.lastScan}</td>
                        <td className="py-3 px-4">
                          <button className="text-indigo-600 hover:text-indigo-800 text-sm">
                            {source.status === 'Connected' ? 'Scan Now' : 'Connect'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <button className="mt-4 text-sm text-indigo-600 hover:text-indigo-800">
                + Add New Source
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
