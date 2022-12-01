import "./ThreadWindow.css";

import ThreadPicker from "./ThreadPicker";
import Step from "./Step";
import { useState } from "react";

export default function ThreadWindow() {
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  return (
    <div className="command-form">
      <ThreadPicker thread={selectedThreadId} setThread={setSelectedThreadId} />

      <Step thread={selectedThreadId} />
    </div>
  );
}
