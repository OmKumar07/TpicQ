import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

function App() {
  const [topics, setTopics] = useState([]);
  const [newTopicName, setNewTopicName] = useState('');
  const [selectedTopic, setSelectedTopic] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);

  // Load topics on component mount
  useEffect(() => {
    loadTopics();
  }, []);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  const loadTopics = async () => {
    try {
      const response = await axios.get(`${API_BASE}/topics`);
      setTopics(response.data);
    } catch (err) {
      setError('Failed to load topics: ' + (err.response?.data?.detail || err.message));
    }
  };

  const createTopic = async (e) => {
    e.preventDefault();
    if (!newTopicName.trim()) {
      setError('Please enter a topic name');
      return;
    }

    try {
      await axios.post(`${API_BASE}/topics`, { name: newTopicName.trim() });
      setSuccess(`Topic "${newTopicName}" created successfully!`);
      setNewTopicName('');
      loadTopics();
    } catch (err) {
      setError('Error creating topic: ' + (err.response?.data?.detail || err.message));
    }
  };

  const generateQuiz = async (e) => {
    e.preventDefault();
    if (!selectedTopic || !difficulty) {
      setError('Please select both topic and difficulty');
      return;
    }

    setLoading(true);
    setQuiz(null);
    setSelectedAnswers({});
    setShowAnswers(false);

    try {
      const response = await axios.post(
        `${API_BASE}/topics/${selectedTopic}/generate-quiz`,
        { difficulty }
      );
      setQuiz(response.data.content);
      setSuccess('Quiz generated successfully!');
    } catch (err) {
      setError('Error generating quiz: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const selectAnswer = (questionIndex, optionIndex) => {
    if (showAnswers) return; // Don't allow changes after showing answers
    
    setSelectedAnswers(prev => ({
      ...prev,
      [questionIndex]: optionIndex
    }));
  };

  const submitQuiz = () => {
    setShowAnswers(true);
    
    // Calculate score
    let correct = 0;
    quiz.questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.answer_index) {
        correct++;
      }
    });
    
    setSuccess(`Quiz completed! Score: ${correct}/${quiz.questions.length} (${Math.round(correct/quiz.questions.length*100)}%)`);
  };

  const resetQuiz = () => {
    setSelectedAnswers({});
    setShowAnswers(false);
    setQuiz(null);
  };

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-md-10 mx-auto">
          <h1 className="text-center mb-4">🧠 TpicQ - Practice Quiz Generator</h1>
          <p className="text-center text-muted">Add topics and generate practice quizzes using Gemini AI</p>

          {/* Error Alert */}
          {error && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              {error}
              <button type="button" className="btn-close" onClick={() => setError('')}></button>
            </div>
          )}

          {/* Success Alert */}
          {success && (
            <div className="alert alert-success alert-dismissible fade show" role="alert">
              {success}
              <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
            </div>
          )}

          {/* Add Topic Section */}
          <div className="card mb-4">
            <div className="card-header">
              <h3>📚 Add New Topic</h3>
            </div>
            <div className="card-body">
              <form onSubmit={createTopic}>
                <div className="mb-3">
                  <label htmlFor="topicName" className="form-label">Topic Name</label>
                  <input
                    type="text"
                    className="form-control"
                    id="topicName"
                    placeholder="e.g., React Hooks, Data Structures, Machine Learning"
                    value={newTopicName}
                    onChange={(e) => setNewTopicName(e.target.value)}
                    required
                  />
                </div>
                <button type="submit" className="btn btn-primary">
                  <i className="bi bi-plus-circle"></i> Add Topic
                </button>
              </form>
            </div>
          </div>

          {/* Topics List */}
          <div className="card mb-4">
            <div className="card-header">
              <h3>📂 Available Topics ({topics.length})</h3>
            </div>
            <div className="card-body">
              {topics.length === 0 ? (
                <p className="text-muted">No topics available. Add some topics to get started!</p>
              ) : (
                <div>
                  {topics.map(topic => (
                    <span
                      key={topic.id}
                      className="badge bg-secondary me-2 mb-2 topic-badge"
                      style={{ fontSize: '0.9em', padding: '0.5em 0.75em' }}
                      onClick={() => setSelectedTopic(topic.id.toString())}
                    >
                      {topic.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quiz Generation Section */}
          <div className="card mb-4">
            <div className="card-header">
              <h3>🎯 Generate Quiz</h3>
            </div>
            <div className="card-body">
              <form onSubmit={generateQuiz}>
                <div className="row">
                  <div className="col-md-6 mb-3">
                    <label htmlFor="selectedTopic" className="form-label">Select Topic</label>
                    <select
                      className="form-select"
                      id="selectedTopic"
                      value={selectedTopic}
                      onChange={(e) => setSelectedTopic(e.target.value)}
                      required
                    >
                      <option value="">Choose a topic...</option>
                      {topics.map(topic => (
                        <option key={topic.id} value={topic.id}>{topic.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="col-md-6 mb-3">
                    <label htmlFor="difficulty" className="form-label">Difficulty Level</label>
                    <select
                      className="form-select"
                      id="difficulty"
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value)}
                      required
                    >
                      <option value="">Choose difficulty...</option>
                      <option value="easy">🟢 Easy (3-4 questions)</option>
                      <option value="medium">🟡 Medium (5-6 questions)</option>
                      <option value="hard">🔴 Hard (7-8 questions)</option>
                    </select>
                  </div>
                </div>
                <button type="submit" className="btn btn-success" disabled={loading}>
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Generating Quiz...
                    </>
                  ) : (
                    <>⚡ Generate Quiz</>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Loading Spinner */}
          {loading && (
            <div className="loading">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="mt-2">🤖 AI is generating your quiz...</p>
            </div>
          )}

          {/* Quiz Display Section */}
          {quiz && (
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h3>📝 {quiz.title}</h3>
                <div>
                  {!showAnswers && (
                    <button className="btn btn-warning me-2" onClick={submitQuiz}>
                      Submit Quiz
                    </button>
                  )}
                  <button className="btn btn-secondary" onClick={resetQuiz}>
                    New Quiz
                  </button>
                </div>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <span className="badge bg-info me-2">Difficulty: {quiz.difficulty}</span>
                  <span className="badge bg-primary">{quiz.questions.length} Questions</span>
                </div>
                
                {quiz.questions.map((question, questionIndex) => (
                  <div key={questionIndex} className="quiz-question">
                    <h5>Question {questionIndex + 1}</h5>
                    <p><strong>{question.q}</strong></p>
                    <div className="options">
                      {question.options.map((option, optionIndex) => {
                        const isSelected = selectedAnswers[questionIndex] === optionIndex;
                        const isCorrect = optionIndex === question.answer_index;
                        const shouldShowCorrect = showAnswers && isCorrect;
                        const shouldShowWrong = showAnswers && isSelected && !isCorrect;
                        
                        let className = 'option';
                        if (shouldShowCorrect) className += ' correct-answer';
                        else if (shouldShowWrong) className += ' bg-danger text-white';
                        else if (isSelected && !showAnswers) className += ' selected-option';

                        return (
                          <div
                            key={optionIndex}
                            className={className}
                            onClick={() => selectAnswer(questionIndex, optionIndex)}
                            style={{ 
                              cursor: showAnswers ? 'default' : 'pointer',
                              border: isSelected && !showAnswers ? '2px solid #0d6efd' : '1px solid #dee2e6'
                            }}
                          >
                            {String.fromCharCode(65 + optionIndex)}. {option}
                            {shouldShowCorrect && ' ✅'}
                            {shouldShowWrong && ' ❌'}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}

                {showAnswers && (
                  <div className="mt-4 p-3 bg-light rounded">
                    <h5>📊 Quiz Results</h5>
                    <p>
                      Correct Answers: {quiz.questions.filter((q, i) => selectedAnswers[i] === q.answer_index).length} / {quiz.questions.length}
                    </p>
                    <div className="progress mb-2" style={{ height: '25px' }}>
                      <div 
                        className="progress-bar" 
                        role="progressbar" 
                        style={{ 
                          width: `${(quiz.questions.filter((q, i) => selectedAnswers[i] === q.answer_index).length / quiz.questions.length) * 100}%` 
                        }}
                      >
                        {Math.round((quiz.questions.filter((q, i) => selectedAnswers[i] === q.answer_index).length / quiz.questions.length) * 100)}%
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Footer */}
          <footer className="text-center mt-5 mb-3">
            <small className="text-muted">
              Powered by <strong>FastAPI</strong>, <strong>React</strong>, and <strong>Gemini AI</strong> 🚀
            </small>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;
