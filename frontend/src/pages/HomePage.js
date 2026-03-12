import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createSession } from "../services/api";
import { LANGUAGE_OPTIONS } from "../constants/languages";
import "./HomePage.css";

const HomePage = () => {
  const [title, setTitle] = useState("");
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleCreateSession = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const session = await createSession(title || undefined, language);
      navigate(`/session/${session.session_code}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create session");
      setLoading(false);
    }
  };

  return (
    <div className="homepage">
      <div className="homepage-container">
        <h1 className="homepage-title">CodeDojo</h1>
        <p className="homepage-subtitle">
          Collaborative coding interview practice platform
        </p>

        <form onSubmit={handleCreateSession} className="session-form">
          <div className="form-group">
            <label htmlFor="title">Session Title (Optional)</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Interview with John Doe"
            />
          </div>

          <div className="form-group">
            <label htmlFor="language">Programming Language</label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {LANGUAGE_OPTIONS.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={loading} className="create-button">
            {loading ? "Creating..." : "Create Session"}
          </button>
        </form>

        <div className="homepage-info">
          <h2>How it works:</h2>
          <ol>
            <li>Create a new session</li>
            <li>Share the link with candidates</li>
            <li>Code together in real-time</li>
            <li>Execute code safely in the browser</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
