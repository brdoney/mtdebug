import useSWR from "swr";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function Step({ thread }) {
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

  return (
    <div className="Step">
      <header className="Step-info">
        <h1>Debug actions: </h1>
        <button disabled={error} name="submit" value="step">
          step
        </button>
        <button disabled={error} name="submit" value="next">
          next
        </button>
        <button disabled={error} name="submit" value="finish">
          finish
        </button>
        <button disabled={error} name="submit" value="continue">
          continue
        </button>
        <button disabled={error} name="submit" value="stop">
          stop
        </button>
        <p>
          <code>{message}</code>
        </p>
      </header>
    </div>
  );
}
