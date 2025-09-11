import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";

// Predefined topics list
const AVAILABLE_TOPICS = [
  "JavaScript",
  "Python",
  "React",
  "Node.js",
  "Data Structures",
  "Algorithms",
  "HTML/CSS",
  "Database",
  "Machine Learning",
  "Web Development",
  "Software Engineering",
  "Computer Networks",
];

function App() {
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [manualTopic, setManualTopic] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);

  // Auto-clear messages
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(""), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const toggleTopicSelection = (topic) => {
    setSelectedTopics((prev) => {
      if (prev.includes(topic)) {
        return prev.filter((t) => t !== topic);
      } else if (prev.length < 3) {
        return [...prev, topic];
      } else {
        setError("You can select maximum 3 topics");
        return prev;
      }
    });
  };

  const addManualTopic = (e) => {
    e.preventDefault();
    if (!manualTopic.trim()) {
      setError("Please enter a topic name");
      return;
    }

    if (selectedTopics.includes(manualTopic.trim())) {
      setError("Topic already selected");
      return;
    }

    if (selectedTopics.length >= 3) {
      setError("You can select maximum 3 topics");
      return;
    }

    setSelectedTopics((prev) => [...prev, manualTopic.trim()]);
    setManualTopic("");
    setSuccess(`Topic "${manualTopic.trim()}" added!`);
  };

  const removeSelectedTopic = (topic) => {
    setSelectedTopics((prev) => prev.filter((t) => t !== topic));
  };

  const getQuestionCount = () => {
    // Each topic generates 10 questions regardless of difficulty
    return 10 * selectedTopics.length;
  };

  const generateQuiz = async (e) => {
    e.preventDefault();
    if (selectedTopics.length === 0 || !difficulty) {
      setError("Please select at least one topic and difficulty level");
      return;
    }

    setLoading(true);
    setQuiz(null);
    setSelectedAnswers({});
    setShowAnswers(false);

    try {
      // For multiple topics, we'll create a combined quiz by calling the API for each topic
      const questionCount = getQuestionCount();

      const topicPromises = selectedTopics.map(async (topic) => {
        // First, try to create the topic in the backend (it will ignore if exists)
        try {
          await axios.post(`${API_BASE}/topics`, { name: topic });
        } catch (topicError) {
          // Ignore if topic already exists (400 error is expected)
          if (topicError.response?.status !== 400) {
            throw new Error(
              `Failed to create topic "${topic}": ${topicError.message}`
            );
          }
        }

        // Wait a small moment for database to be consistent
        await new Promise(resolve => setTimeout(resolve, 100));

        // Get the topic ID with retry logic
        let topicsResponse;
        let attempts = 0;
        const maxAttempts = 3;
        
        while (attempts < maxAttempts) {
          try {
            topicsResponse = await axios.get(`${API_BASE}/topics`);
            break;
          } catch (error) {
            attempts++;
            if (attempts >= maxAttempts) throw error;
            await new Promise(resolve => setTimeout(resolve, 200));
          }
        }
        
        console.log(`Available topics:`, topicsResponse.data);
        
        const topicData = topicsResponse.data.find(
          (t) => t.name.toLowerCase() === topic.toLowerCase()
        );

        console.log(`Looking for topic: "${topic}", found:`, topicData);

        if (!topicData) {
          // Try to find topic with partial match as fallback
          const partialMatch = topicsResponse.data.find(
            (t) => t.name.toLowerCase().includes(topic.toLowerCase()) || 
                   topic.toLowerCase().includes(t.name.toLowerCase())
          );
          
          if (partialMatch) {
            console.log(`Using partial match for topic:`, partialMatch);
            // Use the partial match
            const quizResponse = await axios.post(
              `${API_BASE}/topics/${partialMatch.id}/generate-quiz`,
              { difficulty }
            );

            return {
              topic: partialMatch.name, // Use the actual topic name from database
              questions: quizResponse.data.content.questions,
            };
          }
          
          throw new Error(`Topic "${topic}" not found after creation. Available topics: ${topicsResponse.data.map(t => t.name).join(', ')}`);
        }

        // Generate quiz for this topic
        const quizResponse = await axios.post(
          `${API_BASE}/topics/${topicData.id}/generate-quiz`,
          { difficulty }
        );

        return {
          topic: topic,
          questions: quizResponse.data.content.questions, // Use all 10 questions
        };
      });

      const topicResults = await Promise.all(topicPromises);

      // Combine all questions
      const allQuestions = [];
      topicResults.forEach((result) => {
        result.questions.forEach((question) => {
          allQuestions.push({
            ...question,
            topic: result.topic,
          });
        });
      });

      // Shuffle questions for variety
      const shuffledQuestions = allQuestions.sort(() => Math.random() - 0.5);

      const combinedQuiz = {
        title: `Multi-Topic Quiz: ${selectedTopics.join(", ")}`,
        difficulty: difficulty,
        topics: selectedTopics,
        questions: shuffledQuestions.slice(0, questionCount),
      };

      setQuiz(combinedQuiz);
      setSuccess(
        `Quiz generated with ${combinedQuiz.questions.length} questions from ${selectedTopics.length} topic(s)!`
      );
    } catch (err) {
      console.error("Quiz generation error:", err);

      // Provide more specific error messages
      let errorMessage = "AI failed to respond. Please try again later.";

      if (err.code === "NETWORK_ERROR" || !navigator.onLine) {
        errorMessage = "Network error. Please check your internet connection.";
      } else if (err.response?.status === 404) {
        errorMessage =
          "API endpoint not found. Please check if the server is running.";
      } else if (err.response?.status === 500) {
        errorMessage = "Server error. Please try again later.";
      } else if (err.response?.data?.detail) {
        errorMessage = `API Error: ${err.response.data.detail}`;
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
    setShowAnswers(true);
    const correct = quiz.questions.filter(
      (q, i) => selectedAnswers[i] === q.answer_index
    ).length;
    setSuccess(
      `Quiz completed! Score: ${correct}/${quiz.questions.length} (${Math.round(
        (correct / quiz.questions.length) * 100
      )}%)`
    );
  };

  const resetQuiz = () => {
    setSelectedAnswers({});
    setShowAnswers(false);
    setQuiz(null);
    setSelectedTopics([]);
    setDifficulty("");
  };

  return (
    <div className="container py-4">
      {/* Header */}
      <div className="text-center mb-4 py-4">
        <h1 className="display-4 fw-bold text-primary mb-2">TpicQ</h1>
        <p className="lead text-muted">Multi-Topic Practice Quiz Generator</p>
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

      {/* Success Alert */}
      {success && (
        <div className="alert alert-success alert-dismissible" role="alert">
          {success}
          <button
            type="button"
            className="btn-close"
            onClick={() => setSuccess("")}
            aria-label="Close"
          ></button>
        </div>
      )}

      {/* Topic Selection */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="card-title mb-0">Select Topics (Max 3)</h5>
        </div>
        <div className="card-body">
          {/* Manual Topic Entry */}
          <form onSubmit={addManualTopic} className="mb-4 pb-3 border-bottom">
            <div className="mb-3">
              <label htmlFor="manualTopic" className="form-label fw-semibold">
                Add Custom Topic
              </label>
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  id="manualTopic"
                  placeholder="Enter any topic (e.g., Vue.js, Docker, etc.)"
                  value={manualTopic}
                  onChange={(e) => setManualTopic(e.target.value)}
                />
                <button type="submit" className="btn btn-outline-secondary">
                  Add
                </button>
              </div>
            </div>
          </form>

          {/* Predefined Topics */}
          <div>
            <label className="form-label fw-semibold">
              Or choose from popular topics:
            </label>
            <div className="d-flex flex-wrap gap-2 mt-2">
              {AVAILABLE_TOPICS.map((topic) => (
                <button
                  key={topic}
                  className={`btn btn-sm ${
                    selectedTopics.includes(topic)
                      ? "btn-primary"
                      : "btn-outline-primary"
                  }`}
                  onClick={() => toggleTopicSelection(topic)}
                  disabled={
                    !selectedTopics.includes(topic) &&
                    selectedTopics.length >= 3
                  }
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          {/* Selected Topics Display */}
          {selectedTopics.length > 0 && (
            <div className="mt-4">
              <label className="form-label fw-semibold">
                Selected Topics ({selectedTopics.length}/3):
              </label>
              <div className="d-flex flex-wrap gap-2 mt-2">
                {selectedTopics.map((topic) => (
                  <span
                    key={topic}
                    className="badge bg-primary fs-6 d-flex align-items-center gap-1"
                  >
                    {topic}
                    <button
                      className="btn-close btn-close-white"
                      style={{ fontSize: "0.7rem" }}
                      onClick={() => removeSelectedTopic(topic)}
                      aria-label="Remove topic"
                    ></button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quiz Generator */}
      <div className="card mb-4">
        <div className="card-header">
          <h5 className="card-title mb-0">Generate Quiz</h5>
        </div>
        <div className="card-body">
          <form onSubmit={generateQuiz}>
            <div className="mb-3">
              <label htmlFor="difficulty" className="form-label fw-semibold">
                Difficulty Level
              </label>
              <select
                className="form-select"
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                required
              >
                <option value="">Choose difficulty...</option>
                <option value="easy">
                  Easy (Basic concepts & definitions)
                </option>
                <option value="medium">
                  Medium (Applied knowledge & analysis)
                </option>
                <option value="hard">
                  Hard (Complex scenarios & critical thinking)
                </option>
              </select>
            </div>
            <button
              type="submit"
              className="btn btn-success btn-lg"
              disabled={loading || selectedTopics.length === 0}
            >
              {loading ? (
                <>
                  <span
                    className="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  Generating Quiz...
                </>
              ) : (
                `Generate Quiz (${selectedTopics.length * 10} questions)`
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div className="text-center py-5">
          <div className="spinner-border text-primary mb-3" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="text-muted">
            AI is generating your multi-topic quiz...
          </p>
        </div>
      )}

      {/* Quiz Display */}
      {quiz && (
        <div className="card mb-4 shadow-sm">
          <div className="card-header bg-primary text-white">
            <div className="d-flex justify-content-between align-items-center flex-wrap">
              <div>
                <h5 className="card-title mb-1 text-white">{quiz.title}</h5>
                <div className="d-flex flex-wrap gap-2 mt-2">
                  <span className="badge bg-light text-dark">
                    <i className="bi bi-gear-fill me-1"></i>
                    {quiz.difficulty.charAt(0).toUpperCase() +
                      quiz.difficulty.slice(1)}
                  </span>
                  <span className="badge bg-light text-dark">
                    <i className="bi bi-question-circle-fill me-1"></i>
                    {quiz.questions.length} Questions
                  </span>
                  <span className="badge bg-light text-dark">
                    <i className="bi bi-tags-fill me-1"></i>
                    {quiz.topics.join(", ")}
                  </span>
                </div>
              </div>
              <button
                className="btn btn-outline-light btn-sm"
                onClick={resetQuiz}
              >
                <i className="bi bi-arrow-clockwise me-1"></i>
                Start Over
              </button>
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
                      {question.topic && (
                        <div className="mb-2">
                          <span className="badge bg-secondary bg-opacity-25 text-dark">
                            <i className="bi bi-tag-fill me-1"></i>
                            {question.topic}
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
                      } else if (showAnswers && isCorrect) {
                        buttonClass += " btn-outline-success border-success";
                        iconClass = "bi bi-check-circle text-success me-2";
                      } else {
                        buttonClass += " btn-outline-secondary";
                        iconClass = "";
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
                              boxShadow:
                                isSelected && !showAnswers
                                  ? "0 0 0 0.2rem rgba(13, 110, 253, 0.25)"
                                  : "none",
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

            {/* Submit Quiz Section */}
            {!showAnswers && (
              <div className="card mt-4 border-0 bg-light">
                <div className="card-body text-center py-4">
                  <div className="mb-3">
                    <div className="d-flex justify-content-center align-items-center gap-4 mb-3">
                      <div className="text-center">
                        <div className="h4 mb-1 text-primary fw-bold">
                          {Object.keys(selectedAnswers).length}
                        </div>
                        <small className="text-muted fw-medium">Answered</small>
                      </div>
                      <div className="vr"></div>
                      <div className="text-center">
                        <div className="h4 mb-1 text-secondary fw-bold">
                          {quiz.questions.length -
                            Object.keys(selectedAnswers).length}
                        </div>
                        <small className="text-muted fw-medium">
                          Remaining
                        </small>
                      </div>
                    </div>
                  </div>

                  {Object.keys(selectedAnswers).length <
                  quiz.questions.length ? (
                    <div>
                      <p className="text-muted mb-3 fw-medium">
                        <i className="bi bi-info-circle me-2"></i>
                        Please answer all questions before submitting
                      </p>
                      <button
                        className="btn btn-outline-primary btn-lg px-4"
                        disabled
                      >
                        <i className="bi bi-lock-fill me-2"></i>
                        Submit Quiz
                      </button>
                    </div>
                  ) : (
                    <div>
                      <p className="text-success mb-3 fw-medium">
                        <i className="bi bi-check-circle me-2"></i>
                        Great! All questions answered
                      </p>
                      <button
                        className="btn btn-success btn-lg px-5 shadow-sm"
                        onClick={submitQuiz}
                        style={{ transition: "all 0.2s ease" }}
                      >
                        <i className="bi bi-arrow-right-circle me-2"></i>
                        Submit Quiz
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quiz Results */}
            {showAnswers && (
              <div className="card mt-4 border-0 shadow-sm">
                <div
                  className="card-header bg-gradient text-white"
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
                    <div className="row g-0 text-center">
                      <div className="col-4">
                        <div className="h2 mb-1 text-white fw-bold">
                          {
                            quiz.questions.filter(
                              (q, i) => selectedAnswers[i] === q.answer_index
                            ).length
                          }
                        </div>
                        <small className="text-white-50">Score</small>
                      </div>
                      <div className="col-4">
                        <div className="h2 mb-1 text-white fw-bold">
                          {Math.round(
                            (quiz.questions.filter(
                              (q, i) => selectedAnswers[i] === q.answer_index
                            ).length /
                              quiz.questions.length) *
                              100
                          )}
                          %
                        </div>
                        <small className="text-white-50">Accuracy</small>
                      </div>
                      <div className="col-4">
                        <div className="h2 mb-1 text-white fw-bold">
                          {quiz.questions.length}
                        </div>
                        <small className="text-white-50">Total</small>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="card-body p-4">
                  <div className="row g-4 mb-4">
                    <div className="col-md-6">
                      <div className="d-flex align-items-center p-3 bg-success bg-opacity-10 rounded-3 border border-success border-opacity-25">
                        <div className="me-3">
                          <i className="bi bi-check-circle-fill text-success fs-3"></i>
                        </div>
                        <div>
                          <div className="h5 mb-1 text-success fw-bold">
                            {
                              quiz.questions.filter(
                                (q, i) => selectedAnswers[i] === q.answer_index
                              ).length
                            }
                          </div>
                          <small className="text-muted fw-medium">
                            Correct Answers
                          </small>
                        </div>
                      </div>
                    </div>

                    <div className="col-md-6">
                      <div className="d-flex align-items-center p-3 bg-danger bg-opacity-10 rounded-3 border border-danger border-opacity-25">
                        <div className="me-3">
                          <i className="bi bi-x-circle-fill text-danger fs-3"></i>
                        </div>
                        <div>
                          <div className="h5 mb-1 text-danger fw-bold">
                            {quiz.questions.length -
                              quiz.questions.filter(
                                (q, i) => selectedAnswers[i] === q.answer_index
                              ).length}
                          </div>
                          <small className="text-muted fw-medium">
                            Incorrect Answers
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="text-center mb-4">
                    <h6 className="text-muted mb-3 fw-medium">
                      Performance Breakdown
                    </h6>
                    <div className="progress mb-2" style={{ height: "12px" }}>
                      <div
                        className="progress-bar bg-success"
                        role="progressbar"
                        style={{
                          width: `${
                            (quiz.questions.filter(
                              (q, i) => selectedAnswers[i] === q.answer_index
                            ).length /
                              quiz.questions.length) *
                            100
                          }%`,
                          transition: "width 1s ease",
                        }}
                      ></div>
                    </div>
                    <div className="d-flex justify-content-between small text-muted">
                      <span>0%</span>
                      <span className="fw-bold">
                        {Math.round(
                          (quiz.questions.filter(
                            (q, i) => selectedAnswers[i] === q.answer_index
                          ).length /
                            quiz.questions.length) *
                            100
                        )}
                        % Correct
                      </span>
                      <span>100%</span>
                    </div>
                  </div>

                  <div className="text-center">
                    <button
                      className="btn btn-primary btn-lg px-4 me-3 shadow-sm"
                      onClick={resetQuiz}
                      style={{ transition: "all 0.2s ease" }}
                    >
                      <i className="bi bi-arrow-repeat me-2"></i>
                      Try Again
                    </button>
                    <button
                      className="btn btn-outline-secondary btn-lg px-4 shadow-sm"
                      onClick={() => {
                        setQuiz(null);
                        setSelectedAnswers({});
                        setShowAnswers(false);
                      }}
                      style={{ transition: "all 0.2s ease" }}
                    >
                      <i className="bi bi-house me-2"></i>
                      New Quiz
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <footer className="text-center mt-5 py-4">
        <small className="text-muted">made with ☕ and ❤️ by Om</small>
      </footer>
    </div>
  );
}

export default App;
