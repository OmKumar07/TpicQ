import React from 'react';

const TopicForm = ({ newTopicName, setNewTopicName, onSubmit }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h3>Add New Topic</h3>
      </div>
      <div className="card-body">
        <form onSubmit={onSubmit}>
          <div className="form-group">
            <label htmlFor="topicName">Topic Name</label>
            <input
              type="text"
              className="form-control"
              id="topicName"
              placeholder="Enter topic name (e.g., JavaScript, Python, Data Structures)"
              value={newTopicName}
              onChange={(e) => setNewTopicName(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Add Topic
          </button>
        </form>
      </div>
    </div>
  );
};

export default TopicForm;
