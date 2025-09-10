import React from 'react';

const TopicList = ({ topics, selectedTopic, onTopicSelect }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3>Available Topics ({topics.length})</h3>
      </div>
      <div className="card-body">
        {topics.length === 0 ? (
          <p className="text-muted">No topics available. Add some topics to get started.</p>
        ) : (
          <div className="topic-list">
            {topics.map((topic) => (
              <button
                key={topic.id}
                className={`topic-badge ${
                  selectedTopic === topic.id.toString() ? 'selected' : ''
                }`}
                onClick={() => onTopicSelect(
                  selectedTopic === topic.id.toString() ? "" : topic.id.toString()
                )}
              >
                {topic.name}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TopicList;
