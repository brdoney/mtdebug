import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadPicker from "./ThreadPicker";

function App() {
  return (
    <div className="App">
      <GDBTerminal class="terminal" />

      <form className="command-form" action="/api/output" method="POST">
        <ThreadPicker />
        <label>
          Enter Command: <input type="text" name="command" />
        </label>
        <div>
          <input type="submit" value="Submit" />
        </div>
      </form>
    </div>
  );
}

export default App;
