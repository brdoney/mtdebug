import ThreadPicker from "./ThreadPicker";
import Step from "./Step";
import BreakpointForm from "./BreakpointForm";
import StartButton from "./StartButton";
import { useState } from "react";

export default function ThreadWindow() {
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  return (
    <div>
      <div className="command-form">
        <ThreadPicker
          thread={selectedThreadId}
          setThread={setSelectedThreadId}
        />

        <Step thread={selectedThreadId} />

        <div>
          <BreakpointForm />
          <StartButton />
        </div>
      </div>
    </div>
  );
}
