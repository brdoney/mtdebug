import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadPicker from "./ThreadPicker";
import Step from "./Step";

function App() {

  return (
    <div className="App">
      <GDBTerminal class="terminal" />

      <iframe title="command submission" name="command-frame" style={{display:'none',}}></iframe>
      <form className="command-form" action="/api/output" method="POST" target="command-frame">
        <ThreadPicker />
        <Step />
        <label>
          Enter breakpoint: <input type="text" name="breakpoint"/>
        </label>
        <div>
          <button name="submit" value="breakpoint">submit</button>
        <div>
          <p>Click below to start GDB execution of program with breakpoint on main:</p>
          <button name="submit" value="start" > start</button>
        </div>
        <div>
          <p>Select a thread and click to view local variables</p>
          <button name="submit" value="variables" >variables</button>
        </div>
        </div>
      </form>
    </div>
  );
}

export default App;
