import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadWindow from "./ThreadWindow";

function App() {
  return (
    <div className="App">
      <GDBTerminal class="terminal" />
      <div className="windows">
        <ThreadWindow />
        <ThreadWindow />
      </div>
    </div>
  );
}

export default App;
