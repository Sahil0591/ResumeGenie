'use client';

import { useState, useEffect } from 'react';
import { RefreshCw, FileText, Briefcase } from 'lucide-react';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  score: number;
  remote_flag: boolean;
}

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      const res = await fetch('http://localhost:8000/jobs');
      const data = await res.json();
      setJobs(data);
    } catch (error) {
      console.error("Failed to fetch jobs:", error);
    }
  };

  const triggerIngest = async () => {
    setLoading(true);
    try {
      await fetch('http://localhost:8000/ingest', { method: 'POST' });
      // Poll for updates after 2 seconds
      setTimeout(() => {
        fetchJobs();
        setLoading(false);
      }, 2000);
    } catch (error) {
      console.error("Ingest failed:", error);
      setLoading(false);
    }
  };

  const generateResume = async (jobId: string) => {
    setGenerating(jobId);
    try {
      const res = await fetch(`http://localhost:8000/generate/${jobId}`, { method: 'POST' });
      const data = await res.json();
      alert(`Resume generated! ID: ${data.package_id}`);
    } catch (e) {
      alert('Error generating resume');
    }
    setGenerating(null);
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            <Briefcase /> ResumeGenie
          </h1>
          <button
            onClick={triggerIngest}
            disabled={loading}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            <RefreshCw className={loading ? 'animate-spin' : ''} />
            {loading ? 'Scanning...' : 'Scan New Jobs'}
          </button>
        </div>

        <div className="grid gap-4">
          {jobs.map((job) => (
            <div key={job.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{job.title}</h2>
                <p className="text-gray-500">{job.company} • {job.location}</p>
                <div className="mt-2 flex gap-2">
                  {job.remote_flag && (
                    <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">Remote</span>
                  )}
                  <span className="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full">Score: {job.score}</span>
                </div>
              </div>
              <button
                onClick={() => generateResume(job.id)}
                disabled={generating === job.id}
                className="flex items-center gap-2 border border-gray-200 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm font-medium"
              >
                <FileText size={16} />
                {generating === job.id ? 'Writing...' : 'Draft Resume'}
              </button>
            </div>
          ))}
          
          {jobs.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              No jobs found. Click "Scan New Jobs" to start.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
