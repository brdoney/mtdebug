import { useRef } from "react";
import { useWriteGdb } from "./common";

export default function BreakpointForm() {
  const { postJson } = useWriteGdb();
  const bpInput = useRef();

  function submitBreakpoint() {
    postJson("/api/breakpoint", { symbol: bpInput.current.value });
  }

  return (
    <div>
      <label>
        Enter breakpoint: <input type="text" name="breakpoint" ref={bpInput} />
      </label>
      <button onClick={submitBreakpoint}>submit</button>
    </div>
  );
}
