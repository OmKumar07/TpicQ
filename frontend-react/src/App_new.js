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
    <div className="container">
      {/* Header */}
      <div className="header">
        <h1>TpicQ</h1>
        <p>Multi-Topic Practice Quiz Generator</p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-danger">
          <span>{error}</span>
          <button className="alert-close" onClick={() => setError("")}>
            ×
          </button>
        </div>
      )}

      {/* Success Alert */}
      {success && (
        <div className="alert alert-success">
          <span>{success}</span>
          <button className="alert-close" onClick={() => setSuccess("")}>
            ×
          </button>
        </div>
      )}

      {/* Topic Selection */}
      <div className="card">
        <div className="card-header">
          <h3>Select Topics (Max 3)</h3>
        </div>
        <div className="card-body">
          {/* Manual Topic Entry */}
          <form onSubmit={addManualTopic} className="manual-topic-form">
            <div className="form-group">
              <label htmlFor="manualTopic">Add Custom Topic</label>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <input
                  type="text"
                  className="form-control"
                  id="manualTopic"
                  placeholder="Enter any topic (e.g., Vue.js, Docker, etc.)"
                  value={manualTopic}
                  onChange={(e) => setManualTopic(e.target.value)}
                />
                <button type="submit" className="btn btn-secondary">
                  Add
                </button>
              </div>
            </div>
          </form>

          {/* Predefined Topics */}
          <div style={{ marginTop: "1rem" }}>
            <label>Or choose from popular topics:</label>
            <div className="topic-list">
              {AVAILABLE_TOPICS.map((topic) => (
                <button
                  key={topic}
                  className={`topic-badge ${
                    selectedTopics.includes(topic) ? "selected" : ""
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
            <div style={{ marginTop: "1rem" }}>
              <label>Selected Topics ({selectedTopics.length}/3):</label>
              <div className="selected-topics">
                {selectedTopics.map((topic) => (
                  <span key={topic} className="selected-topic">
                    {topic}
                    <button
                      className="remove-topic"
                      onClick={() => removeSelectedTopic(topic)}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quiz Generator */}
      <div className="card">
        <div className="card-header">
          <h3>Generate Quiz</h3>
        </div>
        <div className="card-body">
          <form onSubmit={generateQuiz}>
            <div className="form-group">
              <label htmlFor="difficulty">Difficulty Level</label>
              <select
                className="form-control"
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
              className="btn btn-success"
              disabled={loading || selectedTopics.length === 0}
            >
              {loading
                ? "Generating Quiz..."
                : `Generate Quiz (${getQuestionCount()} questions)`}
            </button>
          </form>
        </div>
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>AI is generating your multi-topic quiz...</p>
        </div>
      )}

      {/* Quiz Display */}
      {quiz && (
        <div className="card">
          <div className="card-header">
            <div className="quiz-header">
              <h3>{quiz.title}</h3>
              <div className="quiz-actions">
                <button className="btn btn-secondary" onClick={resetQuiz}>
                  Start Over
                </button>
              </div>
            </div>
          </div>
          <div className="card-body">
            <div className="quiz-info">
              <span className="badge badge-info">
                Difficulty: {quiz.difficulty}
              </span>
              <span className="badge badge-primary">
                {quiz.questions.length} Questions
              </span>
              <span className="badge badge-success">
                Topics: {quiz.topics.join(", ")}
              </span>
              {!showAnswers && (
                <span className="badge badge-warning">
                  Answered: {Object.keys(selectedAnswers).length}/
                  {quiz.questions.length}
                </span>
              )}
            </div>

            {quiz.questions.map((question, questionIndex) => (
              <div key={questionIndex} className="question-card">
                <div className="question-header">
                  <span className="question-number">Q{questionIndex + 1}</span>
                  <div>
                    <h5>{question.q}</h5>
                    {question.topic && (
                      <small className="topic-indicator">
                        Topic: {question.topic}
                      </small>
                    )}
                  </div>
                </div>
                <div className="options-grid">
                  {question.options.map((option, optionIndex) => {
                    const isSelected =
                      selectedAnswers[questionIndex] === optionIndex;
                    const isCorrect = optionIndex === question.answer_index;
                    const shouldShowCorrect = showAnswers && isCorrect;
                    const shouldShowWrong =
                      showAnswers && isSelected && !isCorrect;

                    let className = "option-button";
                    if (shouldShowCorrect) className += " correct";
                    else if (shouldShowWrong) className += " wrong";
                    else if (isSelected && !showAnswers)
                      className += " selected";

                    return (
                      <button
                        key={optionIndex}
                        className={className}
                        onClick={() => selectAnswer(questionIndex, optionIndex)}
                        disabled={showAnswers}
                      >
                        <span className="option-letter">
                          {String.fromCharCode(65 + optionIndex)}
                        </span>
                        <span className="option-text">{option}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* Submit Button at the end */}
            {!showAnswers &&
              Object.keys(selectedAnswers).length === quiz.questions.length && (
                <div className="submit-section">
                  <button
                    className="btn btn-primary btn-large"
                    onClick={submitQuiz}
                  >
                    Submit Quiz
                  </button>
                </div>
              )}

            {showAnswers && (
              <div className="results-section">
                <h4>Quiz Results</h4>
                <div className="score-display">
                  <div className="score-item">
                    <span className="score-number">
                      {
                        quiz.questions.filter(
                          (q, i) => selectedAnswers[i] === q.answer_index
                        ).length
                      }
                    </span>
                    <span className="score-label">Correct</span>
                  </div>
                  <div className="score-item">
                    <span className="score-number">
                      {quiz.questions.length -
                        quiz.questions.filter(
                          (q, i) => selectedAnswers[i] === q.answer_index
                        ).length}
                    </span>
                    <span className="score-label">Incorrect</span>
                  </div>
                  <div className="score-item">
                    <span className="score-number">
                      {Math.round(
                        (quiz.questions.filter(
                          (q, i) => selectedAnswers[i] === q.answer_index
                        ).length /
                          quiz.questions.length) *
                          100
                      )}
                      %
                    </span>
                    <span className="score-label">Score</span>
                  </div>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${
                        (quiz.questions.filter(
                          (q, i) => selectedAnswers[i] === q.answer_index
                        ).length /
                          quiz.questions.length) *
                        100
                      }%`,
                    }}
                  ></div>
                </div>
                <div className="result-actions">
                  <button className="btn btn-primary" onClick={resetQuiz}>
                    Start New Quiz
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <footer
        className="text-center"
        style={{ marginTop: "3rem", padding: "1rem" }}
      >
        <small className="text-muted">
          Powered by FastAPI, React, and Gemini AI
        </small>
      </footer>
    </div>
  );
}

export default App;
