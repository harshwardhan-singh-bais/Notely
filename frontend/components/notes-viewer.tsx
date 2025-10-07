import React, { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

interface NotesViewerProps {
  jobOrDocId: string;
  type: "video" | "document";
}

const NotesViewer: React.FC<NotesViewerProps> = ({ jobOrDocId, type }) => {
  const [notes, setNotes] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchNotes = async () => {
      setLoading(true);
      setError("");
      try {
        const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const endpoint =
          type === "video"
            ? `${API_BASE_URL}/video/notes/${jobOrDocId}`
            : `${API_BASE_URL}/document/notes/${jobOrDocId}`;
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error("Notes not found");
        const text = await res.text();
        setNotes(text);
      } catch (err: any) {
        setError(err.message || "Failed to load notes");
      } finally {
        setLoading(false);
      }
    };
    fetchNotes();
  }, [jobOrDocId, type]);

  if (loading) return <div>Loading notes...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;
  return (
    <div className="prose max-w-none">
      <ReactMarkdown>{notes}</ReactMarkdown>
    </div>
  );
};

export default NotesViewer;
