import React from "react";

const QuizGenerator = ({
  topics,
  selectedTopic,
  setSelectedTopic,
  difficulty,
  setDifficulty,
  onGenerate,
  loading,
}) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3>Generate Quiz</h3>
      </div>
      <div className="card-body">
        <form onSubmit={onGenerate}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="selectedTopic">Select Topic</label>
              <select
                className="form-control"
                id="selectedTopic"
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                required
              >
                <option value="">Choose a topic...</option>
                {topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </div>
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
                <option value="easy">Easy (3-4 questions)</option>
                <option value="medium">Medium (5-6 questions)</option>
                <option value="hard">Hard (7-8 questions)</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-success" disabled={loading}>
            {loading ? "Generating Quiz..." : "Generate Quiz"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QuizGenerator;
