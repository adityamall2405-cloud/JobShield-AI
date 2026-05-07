import { useState } from "react";
import { predictJob, trainModel } from "./api";

const initialForm = {
  title: "",
  location: "",
  department: "",
  salary_range: "",
  company_profile: "",
  description: "",
  requirements: "",
  benefits: "",
  telecommuting: 0,
  has_company_logo: 0,
  has_questions: 0,
  employment_type: "",
  required_experience: "",
  required_education: "",
  industry: "",
  function: ""
};

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const onChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? Number(checked) : value
    }));
  };

  const onTrain = async () => {
    setMessage("Training model...");
    try {
      const data = await trainModel();
      setMessage(data.message);
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Training failed");
    }
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const data = await predictJob(form);
      setResult(data);
    } catch (error) {
      setMessage(error?.response?.data?.detail || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>JobShield AI</h1>
      <p>Detect fake job postings with ML trust scoring and scam indicators.</p>

      <div className="toolbar">
        <button type="button" onClick={onTrain}>Train/Reload Model</button>
        {message && <span className="message">{message}</span>}
      </div>

      <form onSubmit={onSubmit} className="card">
        <input name="title" placeholder="Job title" value={form.title} onChange={onChange} required />
        <input name="location" placeholder="Location" value={form.location} onChange={onChange} />
        <input name="salary_range" placeholder="Salary range (e.g. 50000-80000)" value={form.salary_range} onChange={onChange} />
        <input name="industry" placeholder="Industry" value={form.industry} onChange={onChange} />
        <textarea name="company_profile" placeholder="Company profile" value={form.company_profile} onChange={onChange} rows={3} />
        <textarea name="description" placeholder="Job description" value={form.description} onChange={onChange} rows={4} />
        <textarea name="requirements" placeholder="Requirements" value={form.requirements} onChange={onChange} rows={4} />
        <textarea name="benefits" placeholder="Benefits" value={form.benefits} onChange={onChange} rows={2} />

        <div className="checks">
          <label><input type="checkbox" name="telecommuting" checked={Boolean(form.telecommuting)} onChange={onChange} /> Remote</label>
          <label><input type="checkbox" name="has_company_logo" checked={Boolean(form.has_company_logo)} onChange={onChange} /> Has company logo</label>
          <label><input type="checkbox" name="has_questions" checked={Boolean(form.has_questions)} onChange={onChange} /> Has screening questions</label>
        </div>

        <button type="submit" disabled={loading}>{loading ? "Analyzing..." : "Analyze Posting"}</button>
      </form>

      {result && (
        <div className="result card">
          <h2>{result.is_fake ? "Potential Fake Posting" : "Likely Legitimate Posting"}</h2>
          <p><strong>Trust Score:</strong> {(result.trust_score * 100).toFixed(1)}%</p>
          <p><strong>Fraud Probability:</strong> {(result.fake_probability * 100).toFixed(1)}%</p>
          <p><strong>Risk Level:</strong> {result.risk_level.toUpperCase()}</p>
          <h3>Scam Indicators</h3>
          <ul>
            {result.indicators.length === 0 && <li>No strong scam indicators found.</li>}
            {result.indicators.map((indicator) => (
              <li key={indicator}>{indicator}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
