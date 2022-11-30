import ThreadPicker from "./ThreadPicker";
import Step from "./Step";
import { useState } from "react";
import { useSWRConfig } from "swr";

export default function ThreadWindow() {
  const [selectedThreadId, setSelectedThreadId] = useState(null);
  const { mutate } = useSWRConfig();

  function invalidateData() {
    console.log("Refreshing")
    mutate("/api/threads");
    mutate(`/api/step/${selectedThreadId}`);
  }

  return (
    <div>
      {/* Used as target to keep form from changing page */}
      <iframe
        title="command submission"
        name="command-frame"
        style={{ display: "none" }}
      ></iframe>

      <form
        className="command-form"
        action="/api/output"
        method="POST"
        target="command-frame"
        onSubmit={invalidateData}
      >
        <ThreadPicker
          thread={selectedThreadId}
          setThread={setSelectedThreadId}
        />

        <Step thread={selectedThreadId} />

        <label>
          Enter breakpoint: <input type="text" name="breakpoint" />
        </label>
        <div>
          <button name="submit" value="breakpoint">
            submit
          </button>
          <div>
            <p>
              Click below to start GDB execution of program with breakpoint on
              main:
            </p>
            <button name="submit" value="start">
              start
            </button>
          </div>
          <div>
            <p>Select a thread and click to view local variables</p>
            <button name="submit" value="variables">
              variables
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
