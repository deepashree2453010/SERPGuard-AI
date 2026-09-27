import { useState } from "react";
import axios from "axios";
import "./App.css";

// ============================================================
// API CONFIGURATION
// ============================================================

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// ============================================================
// APP COMPONENT
// ============================================================

function App() {
  // ----------------------------------------------------------
  // SEARCH STATE
  // ----------------------------------------------------------

  const [query, setQuery] = useState("Java developer fresher");

  const [location, setLocation] = useState(
    "Chennai, Tamil Nadu, India"
  );

  // ----------------------------------------------------------
  // DATA STATE
  // ----------------------------------------------------------

  const [jobs, setJobs] = useState([]);

  const [statistics, setStatistics] = useState(null);

  const [changes, setChanges] = useState(null);

  const [snapshot, setSnapshot] = useState(null);

  // ----------------------------------------------------------
  // UI STATE
  // ----------------------------------------------------------

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [searched, setSearched] = useState(false);

  // ==========================================================
  // SEARCH JOBS
  // ==========================================================

  const searchJobs = async () => {
    const trimmedQuery = query.trim();
    const trimmedLocation = location.trim();

    // --------------------------------------------------------
    // FRONTEND VALIDATION
    // --------------------------------------------------------

    if (!trimmedQuery) {
      setError("Please enter a job search query.");
      return;
    }

    if (!trimmedLocation) {
      setError("Please enter a location.");
      return;
    }

    try {
      // ------------------------------------------------------
      // START LOADING
      // ------------------------------------------------------

      setLoading(true);
      setError("");
      setSearched(true);

      // Clear previous results while searching
      setJobs([]);
      setStatistics(null);
      setChanges(null);
      setSnapshot(null);

      // ------------------------------------------------------
      // API REQUEST
      // ------------------------------------------------------

      const response = await axios.get(
        `${API_BASE_URL}/api/search`,
        {
          params: {
            query: trimmedQuery,
            location: trimmedLocation,
          },

          timeout: 120000,
        }
      );

      // ------------------------------------------------------
      // DEBUG
      // ------------------------------------------------------

      console.log("SERPGuard API Response:", response.data);

      // ------------------------------------------------------
      // VALIDATE RESPONSE
      // ------------------------------------------------------

      if (!response.data || response.data.success !== true) {
        throw new Error(
          "The backend returned an invalid response."
        );
      }

      // ------------------------------------------------------
      // STORE JOB RESULTS
      // ------------------------------------------------------

      setJobs(
        Array.isArray(response.data.jobs)
          ? response.data.jobs
          : []
      );

      // ------------------------------------------------------
      // STORE STATISTICS
      // ------------------------------------------------------

      setStatistics(
        response.data.statistics || null
      );

      // ------------------------------------------------------
      // STORE CHANGE INTELLIGENCE
      // ------------------------------------------------------

      setChanges(
        response.data.changes || null
      );

      // ------------------------------------------------------
      // STORE SNAPSHOT INFORMATION
      // ------------------------------------------------------

      setSnapshot(
        response.data.snapshot || null
      );
    } catch (err) {
      // ------------------------------------------------------
      // LOG ERROR
      // ------------------------------------------------------

      console.error("SERPGuard Search Error:", err);

      // ------------------------------------------------------
      // DEFAULT ERROR
      // ------------------------------------------------------

      let errorMessage =
        "Unable to connect to SERPGuard backend.";

      // ------------------------------------------------------
      // BACKEND ERROR
      // ------------------------------------------------------

      if (err.response) {
        const backendDetail =
          err.response.data?.detail;

        if (backendDetail) {
          errorMessage = `Backend error: ${backendDetail}`;
        } else {
          errorMessage =
            `Backend error: ${err.response.status}`;
        }
      }

      // ------------------------------------------------------
      // NETWORK ERROR
      // ------------------------------------------------------

      else if (err.request) {
        errorMessage =
          "Unable to connect to SERPGuard backend. Make sure FastAPI is running on port 8000.";
      }

      // ------------------------------------------------------
      // TIMEOUT ERROR
      // ------------------------------------------------------

      else if (err.code === "ECONNABORTED") {
        errorMessage =
          "The job search is taking too long. Please try again.";
      }

      // ------------------------------------------------------
      // OTHER ERROR
      // ------------------------------------------------------

      else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);

      setJobs([]);
      setStatistics(null);
      setChanges(null);
      setSnapshot(null);
    } finally {
      // ------------------------------------------------------
      // STOP LOADING
      // ------------------------------------------------------

      setLoading(false);
    }
  };

  // ==========================================================
  // ENTER KEY SEARCH
  // ==========================================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !loading) {
      searchJobs();
    }
  };

  // ==========================================================
  // FORMAT MATCH SCORE
  // ==========================================================

  const getMatchScore = (job) => {
    return job?.match?.match_score ?? 0;
  };

  // ==========================================================
  // MATCH SCORE CLASS
  // ==========================================================

  const getMatchClass = (score) => {
    if (score >= 80) {
      return "excellent";
    }

    if (score >= 60) {
      return "good";
    }

    if (score >= 40) {
      return "moderate";
    }

    return "low";
  };

  // ==========================================================
  // GET APPLY LINK
  // ==========================================================

  const getApplyLink = (job) => {
    // Direct job link
    if (job?.link) {
      return job.link;
    }

    // SerpAPI share link
    if (job?.share_link) {
      return job.share_link;
    }

    // First available application option
    if (
      Array.isArray(job?.apply_options) &&
      job.apply_options.length > 0
    ) {
      return job.apply_options[0]?.link || null;
    }

    return null;
  };

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="app">

      {/* ====================================================
          HEADER
      ==================================================== */}

      <header className="header">

        <div className="logo">
          SERPGuard <span>AI</span>
        </div>

        <div className="status">
          <span className="status-dot">●</span>
          AI Job Intelligence
        </div>

      </header>

      {/* ====================================================
          MAIN CONTENT
      ==================================================== */}

      <main>

        {/* ==================================================
            HERO SECTION
        ================================================== */}

        <section className="hero">

          <h1>
            Find Jobs That{" "}
            <span>Match You.</span>
          </h1>

          <p>
            AI-powered job discovery, semantic matching and
            change intelligence for smarter job searching.
          </p>

        </section>

        {/* ==================================================
            SEARCH SECTION
        ================================================== */}

        <section className="search-card">

          {/* JOB SEARCH */}

          <div className="input-group">

            <label htmlFor="job-query">
              Job Search
            </label>

            <input
              id="job-query"
              type="text"
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="e.g. Java Developer"
              disabled={loading}
            />

          </div>

          {/* LOCATION */}

          <div className="input-group">

            <label htmlFor="job-location">
              Location
            </label>

            <input
              id="job-location"
              type="text"
              value={location}
              onChange={(event) =>
                setLocation(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="e.g. Chennai"
              disabled={loading}
            />

          </div>

          {/* SEARCH BUTTON */}

          <button
            type="button"
            onClick={searchJobs}
            disabled={loading}
          >
            {loading ? "Searching..." : "Search Jobs"}
          </button>

        </section>

        {/* ==================================================
            ERROR MESSAGE
        ================================================== */}

        {error && (

          <div className="error" role="alert">

            <strong>Search failed:</strong>{" "}
            {error}

          </div>

        )}

        {/* ==================================================
            LOADING MESSAGE
        ================================================== */}

        {loading && (

          <div className="loading-message">

            <div className="loading-spinner"></div>

            <p>
              Searching jobs and calculating AI match
              scores...
            </p>

          </div>

        )}

        {/* ==================================================
            SEARCH STATISTICS
        ================================================== */}

        {!loading && statistics && (

          <section className="statistics">

            <div className="stat-card">

              <span className="stat-value">
                {statistics.jobs_received ?? 0}
              </span>

              <span className="stat-label">
                Jobs Found
              </span>

            </div>

            <div className="stat-card">

              <span className="stat-value">
                {statistics.unique_jobs ?? 0}
              </span>

              <span className="stat-label">
                Unique Jobs
              </span>

            </div>

            <div className="stat-card">

              <span className="stat-value">
                {statistics.jobs_analyzed ?? 0}
              </span>

              <span className="stat-label">
                AI Analyzed
              </span>

            </div>

            <div className="stat-card">

              <span className="stat-value">
                {statistics.top_matches ?? 0}
              </span>

              <span className="stat-label">
                Top Matches
              </span>

            </div>

          </section>

        )}

        {/* ==================================================
            JOB RESULTS
        ================================================== */}

        {!loading && jobs.length > 0 && (

          <section className="results">

            {/* RESULTS HEADER */}

            <div className="section-title">

              <div>

                <h2>
                  Job Matches
                </h2>

                <p>
                  AI-ranked opportunities based on your
                  profile
                </p>

              </div>

              <span>
                {jobs.length} jobs found
              </span>

            </div>

            {/* =================================================
                JOB LIST
            ================================================= */}

            <div className="job-list">

              {jobs.map((job, index) => {

                const matchScore =
                  getMatchScore(job);

                const matchClass =
                  getMatchClass(matchScore);

                const applyLink =
                  getApplyLink(job);

                const matchedSkills =
                  job?.match?.matched_skills || [];

                const missingSkills =
                  job?.match?.missing_skills || [];

                return (

                  <article
                    className="job-card"
                    key={
                      job?.job_id ||
                      job?.link ||
                      index
                    }
                  >

                    {/* ======================================
                        JOB HEADER
                    ====================================== */}

                    <div className="job-header">

                      <div className="job-title-section">

                        <h3>
                          {job?.title ||
                            "Unknown Job"}
                        </h3>

                        <p className="company">

                          {job?.company_name ||
                            "Company not specified"}

                        </p>

                      </div>

                      {/* MATCH SCORE */}

                      <div
                        className={`match-score ${matchClass}`}
                      >

                        <strong>
                          {matchScore}%
                        </strong>

                        <small>
                          AI Match
                        </small>

                      </div>

                    </div>

                    {/* ======================================
                        JOB LOCATION
                    ====================================== */}

                    <p className="location">

                      📍{" "}

                      {job?.location ||
                        "Location not specified"}

                    </p>

                    {/* ======================================
                        JOB DESCRIPTION
                    ====================================== */}

                    {job?.description && (

                      <p className="job-description">

                        {job.description}

                      </p>

                    )}

                    {/* ======================================
                        MATCH DETAILS
                    ====================================== */}

                    {job?.match && (

                      <div className="skills">

                        {/* MATCHED SKILLS */}

                        <div>

                          <strong>
                            Matched Skills:
                          </strong>{" "}

                          {matchedSkills.length > 0
                            ? matchedSkills.join(", ")
                            : "No matching skills detected"}

                        </div>

                        {/* MISSING SKILLS */}

                        <div>

                          <strong>
                            Missing Skills:
                          </strong>{" "}

                          {missingSkills.length > 0
                            ? missingSkills.join(", ")
                            : "No major skill gaps detected"}

                        </div>

                      </div>

                    )}

                    {/* ======================================
                        SCORE BREAKDOWN
                    ====================================== */}

                    {job?.match && (

                      <div className="match-breakdown">

                        <span>
                          Rule Match:{" "}
                          <strong>
                            {job.match.rule_score ?? 0}%
                          </strong>
                        </span>

                        <span>
                          Semantic AI:{" "}
                          <strong>
                            {job.match.semantic_score ?? 0}%
                          </strong>
                        </span>

                      </div>

                    )}

                    {/* ======================================
                        JOB ACTIONS
                    ====================================== */}

                    <div className="job-actions">

                      {applyLink ? (

                        <a
                          href={applyLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="apply-button"
                        >
                          View / Apply
                        </a>

                      ) : (

                        <span className="no-link">
                          Application link unavailable
                        </span>

                      )}

                    </div>

                  </article>

                );
              })}

            </div>

          </section>

        )}

        {/* ==================================================
            NO RESULTS
        ================================================== */}

        {!loading &&
          searched &&
          !error &&
          jobs.length === 0 && (

            <section className="empty-state">

              <h2>
                No matching jobs found
              </h2>

              <p>
                Try changing your job title,
                keywords, or location.
              </p>

            </section>

          )}

        {/* ==================================================
            CHANGE INTELLIGENCE
        ================================================== */}

        {!loading &&
          changes &&
          jobs.length > 0 && (

            <section className="changes-section">

              <div className="section-title">

                <div>

                  <h2>
                    Job Change Intelligence
                  </h2>

                  <p>
                    Changes detected since the
                    previous search
                  </p>

                </div>

              </div>

              <div className="change-grid">

                <div className="change-card">

                  <strong>
                    {changes.new?.length || 0}
                  </strong>

                  <span>
                    New Jobs
                  </span>

                </div>

                <div className="change-card">

                  <strong>
                    {changes.removed?.length || 0}
                  </strong>

                  <span>
                    Removed
                  </span>

                </div>

                <div className="change-card">

                  <strong>
                    {changes.unchanged?.length || 0}
                  </strong>

                  <span>
                    Unchanged
                  </span>

                </div>

                <div className="change-card">

                  <strong>
                    {changes.score_changed?.length || 0}
                  </strong>

                  <span>
                    Score Changed
                  </span>

                </div>

              </div>

            </section>

          )}

        {/* ==================================================
            SNAPSHOT INFORMATION
        ================================================== */}

        {snapshot && (

          <div className="snapshot-info">

            <span>
              Snapshot ID:{" "}
              <strong>
                {snapshot.id ?? "N/A"}
              </strong>
            </span>

            {snapshot.previous_id && (

              <span>
                Previous Snapshot:{" "}
                <strong>
                  {snapshot.previous_id}
                </strong>
              </span>

            )}

          </div>

        )}

      </main>

      {/* ====================================================
          FOOTER
      ==================================================== */}

      <footer className="footer">

        <p>
          © {new Date().getFullYear()} SERPGuard AI
        </p>

        <span>
          AI-powered job discovery & intelligence
        </span>

      </footer>

    </div>
  );
}

export default App;