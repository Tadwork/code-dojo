import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import SessionPage from "./pages/SessionPage";
import "./App.css";

const ROUTER_FUTURE_FLAGS = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
};

export function AppRoutes() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/session/:sessionCode" element={<SessionPage />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router future={ROUTER_FUTURE_FLAGS}>
      <AppRoutes />
    </Router>
  );
}

export default App;
