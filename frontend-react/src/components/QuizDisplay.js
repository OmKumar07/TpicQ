import React from "react";

const QuizDisplay = ({
  quiz,
  selectedAnswers,
  onAnswerSelect,
  showAnswers,
  onSubmit,
  onReset,
}) => {
  if (!quiz) return null;

  const correctAnswers = quiz.questions.filter(
    (q, i) => selectedAnswers[i] === q.answer_index
  ).length;
  const percentage = Math.round((correctAnswers / quiz.questions.length) * 100);

  return (
    <div className="card">
      <div className="card-header">
        <div className="quiz-header">
          <h3>{quiz.title}</h3>
          <div className="quiz-actions">
            {!showAnswers && (
              <button
                className="btn btn-warning"
                onClick={onSubmit}
                disabled={
                  Object.keys(selectedAnswers).length !== quiz.questions.length
                }
              >
                Submit Quiz
              </button>
            )}
            <button className="btn btn-secondary" onClick={onReset}>
              New Quiz
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
          {!showAnswers && (
            <span className="badge badge-success">
              Answered: {Object.keys(selectedAnswers).length}/
              {quiz.questions.length}
            </span>
          )}
        </div>

        {quiz.questions.map((question, questionIndex) => (
          <div key={questionIndex} className="question-card">
            <div className="question-header">
              <span className="question-number">Q{questionIndex + 1}</span>
              <h5>{question.q}</h5>
            </div>
            <div className="options-grid">
              {question.options.map((option, optionIndex) => {
                const isSelected =
                  selectedAnswers[questionIndex] === optionIndex;
                const isCorrect = optionIndex === question.answer_index;
                const shouldShowCorrect = showAnswers && isCorrect;
                const shouldShowWrong = showAnswers && isSelected && !isCorrect;

                let className = "option-button";
                if (shouldShowCorrect) className += " correct";
                else if (shouldShowWrong) className += " wrong";
                else if (isSelected && !showAnswers) className += " selected";

                return (
                  <button
                    key={optionIndex}
                    className={className}
                    onClick={() => onAnswerSelect(questionIndex, optionIndex)}
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

        {showAnswers && (
          <div className="results-section">
            <h4>Quiz Results</h4>
            <div className="score-display">
              <div className="score-item">
                <span className="score-number">{correctAnswers}</span>
                <span className="score-label">Correct</span>
              </div>
              <div className="score-item">
                <span className="score-number">
                  {quiz.questions.length - correctAnswers}
                </span>
                <span className="score-label">Incorrect</span>
              </div>
              <div className="score-item">
                <span className="score-number">{percentage}%</span>
                <span className="score-label">Score</span>
              </div>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
            <div className="performance-message">
              {percentage >= 80 && (
                <div className="alert alert-success">
                  Excellent! You have a strong understanding of this topic.
                </div>
              )}
              {percentage >= 60 && percentage < 80 && (
                <div className="alert alert-warning">
                  Good job! You're on the right track.
                </div>
              )}
              {percentage >= 40 && percentage < 60 && (
                <div className="alert alert-info">
                  Keep practicing! More study time will help you improve.
                </div>
              )}
              {percentage < 40 && (
                <div className="alert alert-danger">
                  Consider reviewing the basics of this topic.
                </div>
              )}
            </div>
            <div className="result-actions">
              <button
                className="btn btn-primary"
                onClick={() => {
                  onReset();
                }}
              >
                Generate New Quiz
              </button>
              <button
                className="btn btn-outline-secondary"
                onClick={() => {
                  // Reset answers but keep same quiz
                  window.location.reload();
                }}
              >
                Retake Quiz
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizDisplay;
