import useSWR from "swr";
import { useWriteGdb } from "./common";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function Step({ thread }) {
  const { postJson } = useWriteGdb(thread);

  let { data: output, error } = useSWR(
    thread != null ? `/api/step/${thread}` : null,
    fetcher
  );
  if (thread == null) {
    error = true;
  }

  let message;
  if (output && output.line_num !== -1) {
    message = `${output.line_num}\t${output.curr_line}`;
  } else {
    message = "Program not in execution";
  }

  function submitControl(action) {
    postJson("/api/exec", { action, thread });
  }

  return (
    <div className="Step">
      <header className="Step-info">
        <button disabled={error} onClick={() => submitControl("step")}>
          step
        </button>
        <button disabled={error} onClick={() => submitControl("next")}>
          next
        </button>
        <button disabled={error} onClick={() => submitControl("finish")}>
          finish
        </button>
        <button disabled={error} onClick={() => submitControl("continue")}>
          continue
        </button>
        <button disabled={error} onClick={() => submitControl("stop")}>
          stop
        </button>
        <p>
          <code>{message}</code>
        </p>
      </header>
    </div>
  );
}
