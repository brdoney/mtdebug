import { useWriteGdb } from "./common";

export default function StartButton() {
  const { post } = useWriteGdb();

  function submitStart() {
    post("/api/start");
  }

  return (
    <div>
      <p>
        Click below to start GDB execution of program with breakpoint on main:
      </p>
      <button onClick={submitStart}>start</button>
    </div>
  );
}
