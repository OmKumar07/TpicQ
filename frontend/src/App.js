import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

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
    const baseQuestions = {
      easy: 3,
      medium: 5,
      hard: 7,
    };

    const base = baseQuestions[difficulty] || 3;
    return base * selectedTopics.length;
  };

  const generateMockQuiz = () => {
    const questionCount = getQuestionCount();
    const questions = [];

    for (let i = 0; i < questionCount; i++) {
      const topicIndex = i % selectedTopics.length;
      const currentTopic = selectedTopics[topicIndex];

      questions.push({
        q: `${
          difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
        } question ${
          Math.floor(i / selectedTopics.length) + 1
        } about ${currentTopic}`,
        options: [
          `Option A for ${currentTopic}`,
          `Option B for ${currentTopic}`,
          `Option C for ${currentTopic}`,
          `Option D for ${currentTopic}`,
        ],
        answer_index: i % 4,
        topic: currentTopic,
      });
    }

    return {
      title: `Multi-Topic Quiz: ${selectedTopics.join(", ")}`,
      difficulty: difficulty,
      topics: selectedTopics,
      questions: questions,
    };
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
      const questionsPerTopic = Math.ceil(
        questionCount / selectedTopics.length
      );

      const topicPromises = selectedTopics.map(async (topic) => {
        try {
          // First, try to create the topic in the backend (it will ignore if exists)
          try {
            await axios.post(`${API_BASE}/topics`, { name: topic });
          } catch (topicError) {
            // Ignore if topic already exists
          }

          // Get the topic ID
          const topicsResponse = await axios.get(`${API_BASE}/topics`);
          const topicData = topicsResponse.data.find(
            (t) => t.name.toLowerCase() === topic.toLowerCase()
          );

          if (!topicData) {
            throw new Error(`Topic "${topic}" not found`);
          }

          // Generate quiz for this topic
          const quizResponse = await axios.post(
            `${API_BASE}/topics/${topicData.id}/generate-quiz`,
            { difficulty }
          );

          return {
            topic: topic,
            questions: quizResponse.data.content.questions.slice(
              0,
              questionsPerTopic
            ),
          };
        } catch (error) {
          console.warn(`Failed to generate quiz for topic "${topic}":`, error);
          // Return mock questions as fallback
          return {
            topic: topic,
            questions: Array.from({ length: questionsPerTopic }, (_, i) => ({
              q: `${
                difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
              } question ${i + 1} about ${topic}`,
              options: [
                `Option A for ${topic}`,
                `Option B for ${topic}`,
                `Option C for ${topic}`,
                `Option D for ${topic}`,
              ],
              answer_index: i % 4,
            })),
          };
        }
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
      setError(
        "Error generating quiz: " + (err.response?.data?.detail || err.message)
      );

      // Fallback to mock quiz if API fails
      const mockQuiz = generateMockQuiz();
      setQuiz(mockQuiz);
      setSuccess("Using sample questions (API unavailable)");
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
                  Easy ({selectedTopics.length * 3} questions)
                </option>
                <option value="medium">
                  Medium ({selectedTopics.length * 5} questions)
                </option>
                <option value="hard">
                  Hard ({selectedTopics.length * 7} questions)
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
                `Generate Quiz (${getQuestionCount()} questions)`
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
        <div className="card mb-4">
          <div className="card-header d-flex justify-content-between align-items-center flex-wrap">
            <h5 className="card-title mb-0">{quiz.title}</h5>
            <button className="btn btn-outline-secondary" onClick={resetQuiz}>
              Start Over
            </button>
          </div>
          <div className="card-body">
            <div className="d-flex flex-wrap gap-2 mb-4">
              <span className="badge bg-info">
                Difficulty: {quiz.difficulty}
              </span>
              <span className="badge bg-primary">
                {quiz.questions.length} Questions
              </span>
              <span className="badge bg-success">
                Topics: {quiz.topics.join(", ")}
              </span>
              {!showAnswers && (
                <span className="badge bg-warning">
                  Answered: {Object.keys(selectedAnswers).length}/
                  {quiz.questions.length}
                </span>
              )}
            </div>

            {quiz.questions.map((question, questionIndex) => (
              <div key={questionIndex} className="card mb-3 border-light">
                <div className="card-body">
                  <div className="d-flex align-items-start mb-3">
                    <span className="badge bg-secondary me-3 mt-1">
                      Q{questionIndex + 1}
                    </span>
                    <div className="flex-grow-1">
                      <h6 className="mb-1">{question.q}</h6>
                      {question.topic && (
                        <small className="text-muted fst-italic">
                          Topic: {question.topic}
                        </small>
                      )}
                    </div>
                  </div>
                  <div className="row g-2">
                    {question.options.map((option, optionIndex) => {
                      const isSelected =
                        selectedAnswers[questionIndex] === optionIndex;
                      const isCorrect = optionIndex === question.answer_index;
                      const shouldShowCorrect = showAnswers && isCorrect;
                      const shouldShowWrong =
                        showAnswers && isSelected && !isCorrect;

                      let buttonClass =
                        "btn text-start w-100 d-flex align-items-center";
                      if (shouldShowCorrect) buttonClass += " btn-success";
                      else if (shouldShowWrong) buttonClass += " btn-danger";
                      else if (isSelected && !showAnswers)
                        buttonClass += " btn-primary";
                      else buttonClass += " btn-outline-secondary";

                      return (
                        <div key={optionIndex} className="col-md-6">
                          <button
                            className={buttonClass}
                            onClick={() =>
                              selectAnswer(questionIndex, optionIndex)
                            }
                            disabled={showAnswers}
                          >
                            <span className="badge bg-dark me-2 flex-shrink-0">
                              {String.fromCharCode(65 + optionIndex)}
                            </span>
                            <span className="flex-grow-1">{option}</span>
                          </button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            ))}

            {/* Submit Button at the end */}
            {!showAnswers &&
              Object.keys(selectedAnswers).length === quiz.questions.length && (
                <div className="text-center py-4 bg-light rounded">
                  <button
                    className="btn btn-primary btn-lg px-5"
                    onClick={submitQuiz}
                  >
                    Submit Quiz
                  </button>
                </div>
              )}

            {showAnswers && (
              <div className="bg-light rounded p-4 mt-4">
                <h5 className="mb-4">Quiz Results</h5>
                <div className="row g-3 mb-4">
                  <div className="col-md-4">
                    <div className="text-center bg-white p-3 rounded">
                      <div className="display-6 fw-bold text-primary">
                        {
                          quiz.questions.filter(
                            (q, i) => selectedAnswers[i] === q.answer_index
                          ).length
                        }
                      </div>
                      <div className="text-muted">Correct</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center bg-white p-3 rounded">
                      <div className="display-6 fw-bold text-danger">
                        {quiz.questions.length -
                          quiz.questions.filter(
                            (q, i) => selectedAnswers[i] === q.answer_index
                          ).length}
                      </div>
                      <div className="text-muted">Incorrect</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center bg-white p-3 rounded">
                      <div className="display-6 fw-bold text-success">
                        {Math.round(
                          (quiz.questions.filter(
                            (q, i) => selectedAnswers[i] === q.answer_index
                          ).length /
                            quiz.questions.length) *
                            100
                        )}
                        %
                      </div>
                      <div className="text-muted">Score</div>
                    </div>
                  </div>
                </div>
                <div className="progress mb-4" style={{ height: "10px" }}>
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
                    }}
                    aria-valuenow={
                      (quiz.questions.filter(
                        (q, i) => selectedAnswers[i] === q.answer_index
                      ).length /
                        quiz.questions.length) *
                      100
                    }
                    aria-valuemin="0"
                    aria-valuemax="100"
                  ></div>
                </div>
                <div className="text-center">
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={resetQuiz}
                  >
                    Start New Quiz
                  </button>
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
