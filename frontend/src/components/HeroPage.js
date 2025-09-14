import React from "react";

function HeroPage({ onSelectQuizType }) {
  return (
    <div className="min-vh-100 d-flex align-items-center bg-gradient-primary">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-10 col-xl-8">
            {/* Hero Header */}
            <div className="text-center mb-5">
              <h1 className="display-2 fw-bold mb-4" style={{ color: "white !important" }}>
                TpicQ
                <span className="text-warning">.</span>
              </h1>
              <p className="lead text-white-50 mb-0 fs-4">
                AI-Powered Quiz Platform for Skill Assessment
              </p>
              <p className="text-white-50 fs-5">
                Choose your learning path and test your knowledge
              </p>
            </div>

            {/* Quiz Options */}
            <div className="row g-4 mb-5">
              {/* Resume Quiz Option */}
              <div className="col-md-6">
                <div className="card h-100 shadow-lg border-0 overflow-hidden">
                  <div className="card-body p-5 text-center position-relative">
                    <div className="mb-4">
                      <div className="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: "80px", height: "80px" }}>
                        <i className="bi bi-file-earmark-person-fill text-primary" style={{ fontSize: "2.5rem" }}></i>
                      </div>
                    </div>
                    
                    <h3 className="card-title fw-bold mb-3 text-dark">Resume Quiz</h3>
                    <p className="card-text text-muted mb-4 fs-6">
                      Upload your resume and get a personalized 30-question quiz based on your skills and experience
                    </p>
                    
                    <div className="mb-4">
                      <div className="row g-2 text-start">
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">Personalized skill assessment</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">30 targeted questions</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">PDF & DOCX support</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">Interview preparation</small>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      className="btn btn-primary btn-lg w-100 shadow-sm"
                      onClick={() => onSelectQuizType("resume")}
                    >
                      <i className="bi bi-upload me-2"></i>
                      Upload Resume
                    </button>
                  </div>
                </div>
              </div>

              {/* Custom Quiz Option */}
              <div className="col-md-6">
                <div className="card h-100 shadow-lg border-0 overflow-hidden">
                  <div className="card-body p-5 text-center position-relative">
                    <div className="mb-4">
                      <div className="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: "80px", height: "80px" }}>
                        <i className="bi bi-puzzle-fill text-success" style={{ fontSize: "2.5rem" }}></i>
                      </div>
                    </div>
                    
                    <h3 className="card-title fw-bold mb-3 text-dark">Custom Quiz</h3>
                    <p className="card-text text-muted mb-4 fs-6">
                      Choose your own topics and difficulty level for a customized learning experience
                    </p>
                    
                    <div className="mb-4">
                      <div className="row g-2 text-start">
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">Choose up to 3 topics</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">3 difficulty levels</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">10 questions per topic</small>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center">
                            <i className="bi bi-check-circle-fill text-success me-2"></i>
                            <small className="text-muted">Any subject area</small>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      className="btn btn-success btn-lg w-100 shadow-sm"
                      onClick={() => onSelectQuizType("custom")}
                    >
                      <i className="bi bi-gear-fill me-2"></i>
                      Create Custom Quiz
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Features Section */}
            <div className="text-center">
              <div className="row g-4 justify-content-center">
                <div className="col-lg-3 col-md-6">
                  <div className="text-white-50">
                    <h6 className="text-white fw-semibold">AI-Powered</h6>
                    <small>Generated by Gemini AI</small>
                  </div>
                </div>
                <div className="col-lg-3 col-md-6">
                  <div className="text-white-50">
                    <h6 className="text-white fw-semibold">Instant Results</h6>
                    <small>Real-time scoring</small>
                  </div>
                </div>
                <div className="col-lg-3 col-md-6">
                  <div className="text-white-50">
                    <h6 className="text-white fw-semibold">Secure</h6>
                    <small>Your data stays private</small>
                  </div>
                </div>
                <div className="col-lg-3 col-md-6">
                  <div className="text-white-50">
                    <h6 className="text-white fw-semibold">Analytics</h6>
                    <small>Detailed performance insights</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HeroPage;