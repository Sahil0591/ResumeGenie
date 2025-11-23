"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function EditProfile() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jsonValue, setJsonValue] = useState<string>("");

  useEffect(() => {
    fetch("https://resumegenie-wjwk.onrender.com/profile")
      .then((res) => res.json())
      .then((data) => {
        setProfile(data);
        setJsonValue(JSON.stringify(data, null, 2));
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load profile");
        setLoading(false);
      });
  }, []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) {
    const updated = { ...profile, [e.target.name]: e.target.value };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleSummaryChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const updated = { ...profile, summary: e.target.value };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleAchievementChange(idx: number, value: string) {
    const newAchievements = [...(profile.achievements || [])];
    newAchievements[idx] = value;
    const updated = { ...profile, achievements: newAchievements };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addAchievement() {
    const updated = { ...profile, achievements: [...(profile.achievements || []), ""] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removeAchievement(idx: number) {
    const newAchievements = [...(profile.achievements || [])];
    newAchievements.splice(idx, 1);
    const updated = { ...profile, achievements: newAchievements };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handlePatentChange(idx: number, value: string) {
    const newPatents = [...(profile.patents || [])];
    newPatents[idx] = value;
    const updated = { ...profile, patents: newPatents };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addPatent() {
    const updated = { ...profile, patents: [...(profile.patents || []), ""] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removePatent(idx: number) {
    const newPatents = [...(profile.patents || [])];
    newPatents.splice(idx, 1);
    const updated = { ...profile, patents: newPatents };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleSkillChange(idx: number, value: string) {
    const newSkills = [...(profile.skills || [])];
    newSkills[idx] = value;
    const updated = { ...profile, skills: newSkills };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addSkill() {
    const updated = { ...profile, skills: [...(profile.skills || []), ""] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removeSkill(idx: number) {
    const newSkills = [...(profile.skills || [])];
    newSkills.splice(idx, 1);
    const updated = { ...profile, skills: newSkills };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleExpChange(idx: number, field: string, value: string) {
    const newExp = [...(profile.experience || [])];
    newExp[idx][field] = value;
    const updated = { ...profile, experience: newExp };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addExperience() {
    const updated = { ...profile, experience: [...(profile.experience || []), { action: "", context: "", result: "" }] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removeExperience(idx: number) {
    const newExp = [...(profile.experience || [])];
    newExp.splice(idx, 1);
    const updated = { ...profile, experience: newExp };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleEduChange(idx: number, field: string, value: string) {
    const newEdu = [...(profile.education || [])];
    newEdu[idx][field] = value;
    const updated = { ...profile, education: newEdu };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addEducation() {
    const updated = { ...profile, education: [...(profile.education || []), { degree: "", institution: "", year: "" }] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removeEducation(idx: number) {
    const newEdu = [...(profile.education || [])];
    newEdu.splice(idx, 1);
    const updated = { ...profile, education: newEdu };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function handleCertChange(idx: number, value: string) {
    const newCerts = [...(profile.certifications || [])];
    newCerts[idx] = value;
    const updated = { ...profile, certifications: newCerts };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function addCertification() {
    const updated = { ...profile, certifications: [...(profile.certifications || []), ""] };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }
  function removeCertification(idx: number) {
    const newCerts = [...(profile.certifications || [])];
    newCerts.splice(idx, 1);
    const updated = { ...profile, certifications: newCerts };
    setProfile(updated);
    setJsonValue(JSON.stringify(updated, null, 2));
  }

  function handleSave() {
    // Validate JSON before saving
    try {
      const parsed = JSON.parse(jsonValue);
      setProfile(parsed);
      setError(null);
      setSaving(true);
      fetch("https://resumegenie-wjwk.onrender.com/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      })
        .then((res) => {
          if (!res.ok) throw new Error();
          setSaving(false);
        })
        .catch(() => {
          setError("Failed to save profile");
          setSaving(false);
        });
    } catch {
      setError("Invalid JSON");
    }
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-gray-50">Loading profile...</div>;
  if (error) return <div className="min-h-screen flex items-center justify-center text-red-500">{error}</div>;
  if (!profile) return null;

  return (
    <main className="min-h-screen bg-gray-200 p-8">
      <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="absolute left-8 top-8">
          <button
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded text-base font-semibold hover:bg-gray-400 shadow"
            onClick={() => router.push("/")}
            aria-label="Back to Main Page"
          >
            Back
          </button>
        </div>
        <div className="bg-gray-100 rounded-xl shadow p-8">
          <h2 className="text-2xl font-bold mb-6 text-gray-800">Edit Master Profile</h2>
          <label className="block mb-2 font-semibold text-gray-700">Name</label>
          <input
            className="w-full mb-4 p-2 border rounded text-gray-900 bg-white"
            name="name"
            value={profile.name || ""}
            onChange={handleChange}
          />
          <label className="block mb-2 font-semibold text-gray-700">GitHub Username</label>
          <input
            className="w-full mb-4 p-2 border rounded text-gray-900 bg-white"
            name="github_username"
            value={profile.github_username || ""}
            onChange={handleChange}
          />
          <label className="block mb-2 font-semibold text-gray-700">Email</label>
          <input
            className="w-full mb-4 p-2 border rounded text-gray-900 bg-white"
            name="email"
            value={profile.email || ""}
            onChange={handleChange}
          />
          <label className="block mb-2 font-semibold text-gray-700">Phone</label>
          <input
            className="w-full mb-4 p-2 border rounded text-gray-900 bg-white"
            name="phone"
            value={profile.phone || ""}
            onChange={handleChange}
          />
          {/* Summary Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Summary</label>
            <textarea
              className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
              rows={3}
              value={profile.summary || ""}
              onChange={handleSummaryChange}
            />
          </div>
          {/* Achievements Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Achievements</label>
            {profile.achievements && profile.achievements.map((ach: string, idx: number) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 border rounded text-gray-900 bg-white"
                  value={ach}
                  onChange={e => handleAchievementChange(idx, e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removeAchievement(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addAchievement}
              type="button"
            >Add Achievement</button>
          </div>
          {/* Patents Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Patents</label>
            {profile.patents && profile.patents.map((pat: string, idx: number) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 border rounded text-gray-900 bg-white"
                  value={pat}
                  onChange={e => handlePatentChange(idx, e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removePatent(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addPatent}
              type="button"
            >Add Patent</button>
          </div>
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Skills</label>
            {profile.skills && profile.skills.map((skill: string, idx: number) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 border rounded text-gray-900 bg-white"
                  value={skill}
                  onChange={e => handleSkillChange(idx, e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removeSkill(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addSkill}
              type="button"
            >Add Skill</button>
          </div>
          {/* Experience Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Experience</label>
            {profile.experience && profile.experience.map((exp: any, idx: number) => (
              <div key={idx} className="mb-4 p-4 border rounded bg-gray-50">
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Action"
                  value={exp.action}
                  onChange={e => handleExpChange(idx, "action", e.target.value)}
                />
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Context"
                  value={exp.context}
                  onChange={e => handleExpChange(idx, "context", e.target.value)}
                />
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Result"
                  value={exp.result}
                  onChange={e => handleExpChange(idx, "result", e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removeExperience(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addExperience}
              type="button"
            >Add Experience</button>
          </div>
          {/* Education Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Education</label>
            {profile.education && profile.education.map((edu: any, idx: number) => (
              <div key={idx} className="mb-4 p-4 border rounded bg-gray-50">
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Degree"
                  value={edu.degree}
                  onChange={e => handleEduChange(idx, "degree", e.target.value)}
                />
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Institution"
                  value={edu.institution}
                  onChange={e => handleEduChange(idx, "institution", e.target.value)}
                />
                <input
                  className="w-full mb-2 p-2 border rounded text-gray-900 bg-white"
                  placeholder="Year"
                  value={edu.year}
                  onChange={e => handleEduChange(idx, "year", e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removeEducation(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addEducation}
              type="button"
            >Add Education</button>
          </div>
          {/* Certifications Section */}
          <div className="mb-6">
            <label className="block mb-2 font-semibold text-gray-700">Certifications</label>
            {profile.certifications && profile.certifications.map((cert: string, idx: number) => (
              <div key={idx} className="flex gap-2 mb-2">
                <input
                  className="flex-1 p-2 border rounded text-gray-900 bg-white"
                  value={cert}
                  onChange={e => handleCertChange(idx, e.target.value)}
                />
                <button
                  className="bg-red-500 text-white px-2 rounded"
                  onClick={() => removeCertification(idx)}
                  type="button"
                >Remove</button>
              </div>
            ))}
            <button
              className="bg-green-600 text-white px-4 py-1 rounded"
              onClick={addCertification}
              type="button"
            >Add Certification</button>
          </div>
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded w-full"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </div>
        {/* JSON Code Editor */}
        <div className="bg-gray-900 rounded-xl shadow p-8 text-white">
          <h2 className="text-xl font-bold mb-4">Profile JSON</h2>
          <textarea
            className="w-full h-[600px] p-4 rounded bg-gray-800 text-green-300 font-mono text-sm border border-gray-700 resize-none"
            value={jsonValue}
            onChange={e => setJsonValue(e.target.value)}
          />
          {error && (
            <div className="mt-2 text-red-400 font-mono text-xs">{error}</div>
          )}
        </div>
      </div>
    </main>
  );
}