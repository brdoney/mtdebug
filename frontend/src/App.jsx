import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadWindow from "./ThreadWindow";
import BreakpointForm from "./BreakpointForm";
import StartButton from "./StartButton";

function App() {
  return (
    <div className="App">
      <GDBTerminal class="terminal" />

      <div className="controls">
        <BreakpointForm />
        <div className="start-button">
          <StartButton />
        </div>

        <div className="windows">
          <ThreadWindow />
          <ThreadWindow />
        </div>
      </div>
    </div>
  );
}

export default App;
