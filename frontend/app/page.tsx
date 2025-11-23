'use client';

import { useState, useEffect } from 'react';
import React from 'react';
import { RefreshCw, FileText, Briefcase } from 'lucide-react';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  score: number;
  remote_flag: boolean;
  apply_url?: string;
}

export default function Home() {
    const [search, setSearch] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [resumePreview, setResumePreview] = useState<string | null>(null);
  const [resumeDownloadUrl, setResumeDownloadUrl] = useState<string | null>(null);

  const fetchJobs = async () => {
    setError(null);
    try {
      const res = await fetch('https://resumegenie-wjwk.onrender.com/jobs');
      if (!res.ok) throw new Error('Failed to fetch jobs');
      const data = await res.json();
      setJobs(data);
    } catch (error) {
      setError("Failed to fetch jobs. Please try again later.");
      setJobs([]);
      console.error("Failed to fetch jobs:", error);
    }
  };

  const triggerIngest = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('https://resumegenie-wjwk.onrender.com/ingest', { method: 'POST' });
      if (!res.ok) throw new Error('Ingest failed');
      // Poll for updates after 2 seconds
      setTimeout(() => {
        fetchJobs();
        setLoading(false);
      }, 2000);
    } catch (error) {
      setError("Job scan failed. Please try again.");
      setLoading(false);
      console.error("Ingest failed:", error);
    }
  };

    // Top-level utility for consistent filename sanitization
    function sanitizeJobId(jobId: string) {
      // Replace all non-alphanumeric characters with underscores
      return jobId.replace(/[^a-zA-Z0-9]/g, '_');
    }

    const generateResume = async (jobId: string) => {
        setGenerating(jobId);
        setError(null);
        setResumePreview(null);
        setResumeDownloadUrl(null);
        try {
          const encodedId = encodeURIComponent(jobId);
          const res = await fetch(`https://resumegenie-wjwk.onrender.com/generate/${encodedId}`, { method: 'POST' });
          if (!res.ok) throw new Error('Resume generation failed');
          const data = await res.json();
          // Assume backend returns { package_id, preview_md, pdf_url }
          setResumePreview(data.preview_md || '');
          setResumeDownloadUrl(data.pdf_url || null);
        } catch (e) {
          setError('Error generating resume. Please try again.');
        }
        setGenerating(null);
    };

  useEffect(() => {
    fetchJobs();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col gap-4 mb-8">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
              <Briefcase /> ResumeGenie
            </h1>
            <div className="flex flex-row gap-2">
              <a href="/EditProfile">
                <button className="bg-green-600 text-white px-4 py-2 rounded-lg">Edit Profile</button>
              </a>
              <button
                onClick={triggerIngest}
                disabled={loading}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={loading ? 'animate-spin' : ''} />
                {loading ? 'Scanning...' : 'Scan New Jobs'}
              </button>
            </div>
          </div>
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search jobs by title or company..."
            className="border border-gray-300 rounded-lg px-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-200 text-gray-800 placeholder-gray-500"
          />
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg text-center">
            {error}
          </div>
        )}

        {loading && (
          <div className="mb-4 flex justify-center items-center">
            <RefreshCw className="animate-spin text-blue-600" size={32} />
            <span className="ml-2 text-blue-600">Loading...</span>
          </div>
        )}

        <div className="grid gap-4">
          {/* Resume Preview Modal */}
          {(resumePreview || resumeDownloadUrl) && (
            <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-lg max-w-6xl w-full p-16 relative">
                <button
                  className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-4xl font-bold w-10 h-10 flex items-center justify-center z-40"
                  style={{ lineHeight: 1 }}
                  onClick={() => { setResumePreview(null); setResumeDownloadUrl(null); }}
                  aria-label="Close preview"
                >
                  &times;
                </button>
                <h3 className="text-xl text-gray-800 font-bold mb-4">Resume Preview</h3>
                {resumeDownloadUrl ? (
                  <iframe
                    src={`https://resumegenie-wjwk.onrender.com${resumeDownloadUrl}`}
                    width="100%"
                    height="1000px"
                    className="rounded-lg border mb-4"
                    title="Resume PDF Preview"
                  />
                ) : (
                  <div className="prose prose-sm max-h-96 overflow-y-auto mb-4 text-gray-800" style={{ whiteSpace: 'pre-wrap' }}>
                    {resumePreview}
                  </div>
                )}
                {resumeDownloadUrl && (
                  <a
                    href={`https://resumegenie-wjwk.onrender.com${resumeDownloadUrl}`}
                    download
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                  >
                    Download PDF
                  </a>
                )}
              </div>
            </div>
          )}
          {jobs.filter(job =>
            job.title.toLowerCase().includes(search.toLowerCase()) ||
            job.company.toLowerCase().includes(search.toLowerCase())
          ).map((job) => (
            <div key={job.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{job.title}</h2>
                <p className="text-gray-500">{job.company} • {job.location}
                  {job.apply_url && (
                    <a
                      href={job.apply_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 underline text-sm ml-2"
                    >
                      View Job
                    </a>
                  )}
                </p>
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
                className="flex items-center gap-2 border border-gray-400 bg-gray-150 text-black px-4 py-2 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                <FileText size={16} />
                {generating === job.id ? (
                  <>
                    <RefreshCw className="animate-spin text-blue-600" size={16} /> Writing...
                  </>
                ) : 'Draft Resume'}
              </button>
            </div>
          ))}

          {jobs.filter(job =>
            job.title.toLowerCase().includes(search.toLowerCase()) ||
            job.company.toLowerCase().includes(search.toLowerCase())
          ).length === 0 && !loading && (
            <div className="text-center py-12 text-gray-500">
              No jobs found. Try a different search or click "Scan New Jobs" to start.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
