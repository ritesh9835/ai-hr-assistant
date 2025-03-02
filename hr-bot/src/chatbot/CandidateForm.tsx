import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./Form.css";

const CandidateForm = () => {
    const [email, setEmail] = useState("");
    const [jobUrl, setJobUrl] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append("email", email);
        formData.append("job_url", jobUrl);
        if (file) formData.append("file", file);
        await axios.post("http://localhost:8000/submit-candidate", formData);
        navigate(`/chat/${email}`);
    };

    return (
        <form onSubmit={handleSubmit} className="form-container">
            <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            <input type="url" placeholder="Job URL" value={jobUrl} onChange={(e) => setJobUrl(e.target.value)} required />
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
            <button type="submit">Submit</button>
        </form>
    );
};
export default CandidateForm;