import "./App.css";

function App() {
  return (
    <div className="App">
      <form className="command-form" action="/output" method="POST">
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
