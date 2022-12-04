import "./App.css";
import GDBTerminal from "./Terminal";
import ThreadWindow from "./ThreadWindow";

function App() {
  return (
    <div className="App">
      <GDBTerminal class="terminal" />
      <ThreadWindow />
    </div>
  );
}

export default App;
