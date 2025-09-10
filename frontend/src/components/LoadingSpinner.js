import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>AI is generating your quiz...</p>
    </div>
  );
};

export default LoadingSpinner;
