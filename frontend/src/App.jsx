import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadWindow from "./ThreadWindow";
import BreakpointForm from "./BreakpointForm";
import StartButton from "./StartButton";
import MutexView from "./MutexView";

function App() {
  return (
    <div className="App">
      <GDBTerminal class="terminal" />

      <div className="controls">
        <BreakpointForm />
        <StartButton />
        <MutexView />

        <div className="windows">
          <ThreadWindow />
          <ThreadWindow />
        </div>
      </div>
    </div>
  );
}

export default App;
