import React, { useState } from "react";
import HeroPage from "./components/HeroPage";
import ResumeQuiz from "./components/ResumeQuiz";
import CustomQuiz from "./components/CustomQuiz";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState("hero");

  const handleSelectQuizType = (type) => {
    setCurrentView(type);
  };

  const handleBackToHome = () => {
    setCurrentView("hero");
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case "resume":
        return <ResumeQuiz onBack={handleBackToHome} />;
      case "custom":
        return <CustomQuiz onBack={handleBackToHome} />;
      default:
        return <HeroPage onSelectQuizType={handleSelectQuizType} />;
    }
  };

  return <div className="App">{renderCurrentView()}</div>;
}

export default App;
