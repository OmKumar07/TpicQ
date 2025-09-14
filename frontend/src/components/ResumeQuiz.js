import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

function ResumeQuiz({ onBack }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [quiz, setQuiz] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);

  // Debug showAnswers state changes
  useEffect(() => {
    console.log("showAnswers state changed to:", showAnswers);
  }, [showAnswers]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const allowedTypes = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
      ];
      if (!allowedTypes.includes(selectedFile.type)) {
        setError("Please upload a PDF or Word document (.pdf, .docx, .doc)");
        return;
      }

      // Validate file size (max 5MB)
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError("File size must be less than 5MB");
        return;
      }

      setFile(selectedFile);
      setError("");
    }
  };

  const generateResumeQuiz = async () => {
    if (!file) {
      setError("Please select a resume file first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Step 1: Upload resume
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await axios.post(
        `${API_BASE}/api/resume/upload-resume`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      if (!uploadResponse.data || !uploadResponse.data.id) {
        throw new Error("Failed to upload resume");
      }

      // Step 2: Generate quiz
      const quizResponse = await axios.post(
        `${API_BASE}/api/resume/generate-resume-quiz/${uploadResponse.data.id}`
      );

      if (quizResponse.data && quizResponse.data.quiz_content) {
        console.log("Quiz data received:", quizResponse.data.quiz_content);
        setQuiz(quizResponse.data.quiz_content);
        setSelectedAnswers({});
        setShowAnswers(false);
      } else {
        throw new Error("Failed to generate quiz from resume");
      }
    } catch (err) {
      console.error("Resume quiz generation error:", err);

      let errorMessage =
        "Failed to generate quiz from resume. Please try again.";

      if (err.response?.status === 413) {
        errorMessage =
          "File too large. Please upload a smaller resume (max 5MB).";
      } else if (err.response?.status === 400) {
        errorMessage =
          err.response.data?.detail ||
          "Invalid file format. Please upload a PDF or Word document.";
      } else if (err.response?.status === 500) {
        errorMessage = "Server error. Please try again later.";
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const selectAnswer = (questionIndex, optionIndex) => {
    if (showAnswers) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionIndex]: optionIndex,
    }));
  };

  const submitQuiz = () => {
    console.log("Submitting quiz...");
    console.log("Quiz:", quiz);
    console.log("Selected answers:", selectedAnswers);
    console.log("Quiz questions:", quiz?.questions);

    // Validate that we have all required data
    if (!quiz || !quiz.questions) {
      console.error("No quiz data available");
      setError("Quiz data is missing. Please try again.");
      return;
    }

    if (Object.keys(selectedAnswers).length !== quiz.questions.length) {
      console.error("Not all questions answered");
      setError("Please answer all questions before submitting.");
      return;
    }

    console.log("Setting showAnswers to true");
    setShowAnswers(true);
    console.log("ShowAnswers set to true");
  };

  const resetQuiz = () => {
    setFile(null);
    setQuiz(null);
    setSelectedAnswers({});
    setShowAnswers(false);
    setError("");
  };

  const getScore = () => {
    if (!quiz) {
      console.log("No quiz data for scoring");
      return { correct: 0, total: 0, percentage: 0 };
    }
    if (!quiz.questions) {
      console.log("No questions in quiz data");
      return { correct: 0, total: 0, percentage: 0 };
    }

    const correct = quiz.questions.filter(
      (q, i) => selectedAnswers[i] === q.answer_index
    ).length;

    const score = {
      correct,
      total: quiz.questions.length,
      percentage: Math.round((correct / quiz.questions.length) * 100),
    };

    console.log("Score calculated:", score);
    return score;
  };

  return (
    <div className="container py-4">
      {/* Header */}
      <div className="d-flex align-items-center mb-4">
        <button className="btn btn-outline-secondary me-3" onClick={onBack}>
          <i className="bi bi-arrow-left me-2"></i>
          Back
        </button>
        <div>
          <h1 className="h2 fw-bold text-primary mb-1">Resume Quiz</h1>
          <p className="text-muted mb-0">
            Upload your resume for a personalized 30-question assessment
          </p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-danger alert-dismissible" role="alert">
          {error}
          <button
            type="button"
            className="btn-close"
            onClick={() => setError("")}
            aria-label="Close"
          ></button>
        </div>
      )}

      {!quiz && (
        <>
          {/* File Upload Section */}
          <div className="card mb-4">
            <div className="card-body p-5 text-center">
              <div className="mb-4">
                <i
                  className="bi bi-cloud-upload text-primary mb-3"
                  style={{ fontSize: "4rem" }}
                ></i>
                <h5 className="fw-bold mb-2">Upload Your Resume</h5>
                <p className="text-muted">
                  We'll analyze your resume and create personalized quiz
                  questions based on your skills and experience
                </p>
              </div>

              <div className="mb-4">
                <input
                  type="file"
                  id="resumeFile"
                  className="form-control d-none"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                />
                <label
                  htmlFor="resumeFile"
                  className="btn btn-outline-primary btn-lg px-5 mb-3"
                  style={{ cursor: "pointer" }}
                >
                  <i className="bi bi-file-earmark-arrow-up me-2"></i>
                  Choose Resume File
                </label>

                {file && (
                  <div className="mt-3">
                    <div className="d-inline-flex align-items-center bg-light rounded-pill px-3 py-2">
                      <i className="bi bi-file-earmark-text text-primary me-2"></i>
                      <span className="fw-medium">{file.name}</span>
                      <button
                        className="btn btn-sm btn-outline-danger ms-2 rounded-circle"
                        onClick={() => setFile(null)}
                        style={{ width: "24px", height: "24px", padding: "0" }}
                      >
                        <i
                          className="bi bi-x"
                          style={{ fontSize: "0.8rem" }}
                        ></i>
                      </button>
                    </div>
                  </div>
                )}
              </div>

              <div className="mb-4">
                <small className="text-muted">
                  Supported formats: PDF, DOC, DOCX • Max size: 5MB
                </small>
              </div>

              <button
                className="btn btn-primary btn-lg px-5"
                onClick={generateResumeQuiz}
                disabled={!file || loading}
              >
                {loading ? (
                  <>
                    <span
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></span>
                    Analyzing Resume...
                  </>
                ) : (
                  <>
                    <i className="bi bi-magic me-2"></i>
                    Generate Quiz (30 Questions)
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Features */}
          <div className="row g-4">
            <div className="col-md-4">
              <div className="text-center">
                <div
                  className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "60px", height: "60px" }}
                >
                  <i className="bi bi-person-workspace text-primary fs-4"></i>
                </div>
                <h6 className="fw-bold">Skill-Based Questions</h6>
                <p className="text-muted small">
                  Questions tailored to your specific skills and experience
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <div
                  className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "60px", height: "60px" }}
                >
                  <i className="bi bi-speedometer2 text-success fs-4"></i>
                </div>
                <h6 className="fw-bold">Interview Prep</h6>
                <p className="text-muted small">
                  Perfect for preparing for technical interviews
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <div
                  className="bg-warning bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style={{ width: "60px", height: "60px" }}
                >
                  <i className="bi bi-shield-check text-warning fs-4"></i>
                </div>
                <h6 className="fw-bold">Secure & Private</h6>
                <p className="text-muted small">
                  Your resume data is processed securely and not stored
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Loading State */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary mb-3" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="text-muted">
            AI is analyzing your resume and creating personalized questions...
          </p>
        </div>
      )}

      {/* Quiz Display */}
      {quiz && (
        <div className="card shadow-sm">
          <div className="card-header bg-primary text-white">
            <div className="d-flex justify-content-between align-items-center">
              <div>
                <h5 className="card-title mb-1 text-white">
                  Resume-Based Quiz
                </h5>
                <small className="text-white-50">
                  Based on: {quiz.resume_filename || "Your Resume"}
                </small>
              </div>
              <div className="text-end">
                <span className="badge bg-light text-dark me-2">
                  30 Questions
                </span>
                <button
                  className="btn btn-outline-light btn-sm"
                  onClick={resetQuiz}
                >
                  <i className="bi bi-arrow-clockwise me-1"></i>
                  New Quiz
                </button>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          {!showAnswers && (
            <div className="card-body py-2 bg-light">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <small className="text-muted fw-bold">Progress</small>
                <small className="text-muted fw-bold">
                  {Object.keys(selectedAnswers).length} /{" "}
                  {quiz.questions.length}
                </small>
              </div>
              <div className="progress" style={{ height: "8px" }}>
                <div
                  className="progress-bar bg-success"
                  role="progressbar"
                  style={{
                    width: `${
                      (Object.keys(selectedAnswers).length /
                        quiz.questions.length) *
                      100
                    }%`,
                    transition: "width 0.3s ease",
                  }}
                ></div>
              </div>
            </div>
          )}

          <div className="card-body">
            {quiz.questions.map((question, questionIndex) => (
              <div key={questionIndex} className="card mb-4 border-0 shadow-sm">
                <div className="card-body p-4">
                  <div className="d-flex align-items-start mb-4">
                    <div className="me-3">
                      <span
                        className={`badge fs-6 px-3 py-2 ${
                          showAnswers
                            ? selectedAnswers[questionIndex] ===
                              question.answer_index
                              ? "bg-success"
                              : selectedAnswers[questionIndex] !== undefined
                              ? "bg-danger"
                              : "bg-secondary"
                            : selectedAnswers[questionIndex] !== undefined
                            ? "bg-primary"
                            : "bg-secondary"
                        }`}
                      >
                        Q{questionIndex + 1}
                      </span>
                    </div>
                    <div className="flex-grow-1">
                      <h6
                        className="fw-bold mb-2 text-dark"
                        style={{ fontSize: "1.1rem", lineHeight: "1.4" }}
                      >
                        {question.q}
                      </h6>
                      {question.category && (
                        <div className="mb-2">
                          <span className="badge bg-secondary bg-opacity-25 text-dark">
                            <i className="bi bi-tag-fill me-1"></i>
                            {question.category}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="row g-3">
                    {question.options.map((option, optionIndex) => {
                      const isSelected =
                        selectedAnswers[questionIndex] === optionIndex;
                      const isCorrect = optionIndex === question.answer_index;
                      const shouldShowCorrect = showAnswers && isCorrect;
                      const shouldShowWrong =
                        showAnswers && isSelected && !isCorrect;

                      let buttonClass =
                        "btn text-start w-100 d-flex align-items-center p-3 border-2";
                      let iconClass = "";

                      if (shouldShowCorrect) {
                        buttonClass += " btn-success border-success";
                        iconClass = "bi bi-check-circle-fill text-white me-2";
                      } else if (shouldShowWrong) {
                        buttonClass += " btn-danger border-danger";
                        iconClass = "bi bi-x-circle-fill text-white me-2";
                      } else if (isSelected && !showAnswers) {
                        buttonClass += " btn-primary border-primary";
                        iconClass = "bi bi-record-circle-fill text-white me-2";
                      } else {
                        buttonClass += " btn-outline-secondary";
                      }

                      return (
                        <div key={optionIndex} className="col-md-6">
                          <button
                            className={buttonClass}
                            onClick={() =>
                              selectAnswer(questionIndex, optionIndex)
                            }
                            disabled={showAnswers}
                            style={{
                              minHeight: "60px",
                              transition: "all 0.2s ease",
                            }}
                          >
                            {iconClass && <i className={iconClass}></i>}
                            <span className="badge bg-dark text-white me-3 flex-shrink-0">
                              {String.fromCharCode(65 + optionIndex)}
                            </span>
                            <span className="flex-grow-1 fw-medium">
                              {option}
                            </span>
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}

            {/* Submit Section */}
            {!showAnswers && (
              <div className="text-center mt-4">
                {Object.keys(selectedAnswers).length < quiz.questions.length ? (
                  <button
                    className="btn btn-outline-primary btn-lg px-4"
                    disabled
                  >
                    <i className="bi bi-lock-fill me-2"></i>
                    Submit Quiz ({Object.keys(selectedAnswers).length}/
                    {quiz.questions.length})
                  </button>
                ) : (
                  <button
                    className="btn btn-success btn-lg px-5"
                    onClick={submitQuiz}
                  >
                    <i className="bi bi-check-circle me-2"></i>
                    Submit Quiz
                  </button>
                )}
              </div>
            )}

            {/* Results */}
            {showAnswers && (
              <div className="card mt-4 border-0 shadow-sm">
                <div
                  className="card-header text-white"
                  style={{
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  }}
                >
                  <div className="text-center">
                    <h4 className="mb-2 text-white">
                      <i className="bi bi-trophy-fill me-2"></i>
                      Quiz Complete!
                    </h4>
                    <div className="row text-center">
                      <div className="col-4">
                        <div
                          className="h2 mb-1 fw-bold"
                          style={{ color: "white !important" }}
                        >
                          {getScore().correct}
                        </div>
                        <small style={{ color: "rgba(255,255,255,0.8)" }}>
                          Correct
                        </small>
                      </div>
                      <div className="col-4">
                        <div
                          className="h2 mb-1 fw-bold"
                          style={{ color: "white !important" }}
                        >
                          {getScore().percentage}%
                        </div>
                        <small style={{ color: "rgba(255,255,255,0.8)" }}>
                          Score
                        </small>
                      </div>
                      <div className="col-4">
                        <div
                          className="h2 mb-1 fw-bold"
                          style={{ color: "white !important" }}
                        >
                          {getScore().total}
                        </div>
                        <small style={{ color: "rgba(255,255,255,0.8)" }}>
                          Total
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="card-body text-center">
                  <p className="text-muted mb-4">
                    Great job! This assessment was based on the skills and
                    experience from your resume.
                  </p>
                  <button className="btn btn-primary me-3" onClick={resetQuiz}>
                    <i className="bi bi-arrow-repeat me-2"></i>
                    Try Another Resume
                  </button>
                  <button
                    className="btn btn-outline-secondary"
                    onClick={onBack}
                  >
                    <i className="bi bi-house me-2"></i>
                    Back to Home
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResumeQuiz;
