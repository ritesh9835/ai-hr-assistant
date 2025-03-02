import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import "./ChatBot.css";

const ChatBotComponent = () => {
    const { email } = useParams<{ email: string }>();
    const navigate = useNavigate();
    const [messages, setMessages] = useState<string[]>([]);
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [userInput, setUserInput] = useState("");
    const [assessmentComplete, setAssessmentComplete] = useState(false);
    const [score, setScore] = useState<number | null>(null);
    const [summary, setSummary] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [isDisabled, setIsDisabled] = useState(true);

    useEffect(() => {
        const socket = new WebSocket(`ws://localhost:8000/ws/screen/${email}`);
        let isMounted = true;
        socket.onopen = () => {
            console.log("WebSocket connection established");
            setIsDisabled(false);
        };
        socket.onmessage = (event) => {
            const message = event.data;
            setMessages((prev) => [...prev, message]);

            if (message.startsWith("Assessment complete! Score:")) {
                const scoreMatch = message.match(/Score: (\d+)/);
                const summaryMatch = message.match(/Summary: (.+)/);
                if (scoreMatch && summaryMatch) {
                    setScore(parseInt(scoreMatch[1], 10));
                    setSummary(summaryMatch[1]);
                    setAssessmentComplete(true);
                    setIsDisabled(true);
                }
            }
        };
        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
        socket.onclose = (event) => {
            if (event.wasClean) {
                console.log(`WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`);
            } else {
                console.error("WebSocket connection closed unexpectedly");
            }
            setIsDisabled(true);
        };
        if (isMounted) {
            setWs(socket);
        }
        return () => {
            isMounted = false;
            if (socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [email]);

    const sendMessage = () => {
        if (ws && userInput) {
            ws.send(userInput);
            setMessages((prev) => [...prev, `You: ${userInput}`]);
            setUserInput("");
        }
    };

    const handleRedirect = () => {
        navigate("/candidate-form");
    };

    return (
        <>
            <div className="chatbox">
                <div className="chatbox-header">
                    <h2>AI HR Assistant</h2>
                </div>
                <div className="chatbox-messages">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.startsWith("You:") ? "user" : "bot"}`}>
                            <div className="icon">{msg.startsWith("You:") ? "👤" : "🤖"}</div>
                            <div className="text">{msg}</div>
                        </div>
                    ))}
                </div>
                <div className="chatbox-input">
                    <input
                        type="text"
                        value={userInput}
                        onChange={(e) => setUserInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        disabled={isDisabled}
                    />
                    <button onClick={sendMessage} disabled={isDisabled}>Send</button>
                </div>
            </div>

            <div className="chatbox-footer">
                {assessmentComplete && (
                    <div className="assessment-complete">
                        <button className="footer-button success-btn" onClick={() => setShowModal(true)}>Show Response</button>
                        <button className="footer-button" onClick={handleRedirect}>Start Re-assessment</button>
                    </div>
                )}
                {showModal && (
                    <div className="modal">
                        <div className="modal-content">
                            <span className="close" onClick={() => setShowModal(false)}>&times;</span>
                            <h2>Assessment Complete</h2>
                            <p>Score: {score}</p>
                            <p>Summary: {summary}</p>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
};

export default ChatBotComponent;