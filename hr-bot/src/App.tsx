import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import CandidateForm from "./chatbot//CandidateForm";
import ChatBotComponent from "./chatbot/ChatBot";

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<CandidateForm />} />
                <Route path="/chat/:email" element={<ChatBotComponent />} />
            </Routes>
        </Router>
    );
};
export default App;