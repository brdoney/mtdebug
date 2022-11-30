import "./Terminal.css";
import "../node_modules/xterm/css/xterm.css";
import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { AttachAddon } from "xterm-addon-attach";
import { FitAddon } from "xterm-addon-fit";

export default function GDBTerminal() {
  const termDiv = useRef(null);

  useEffect(() => {
    const term = new Terminal();
    const fitAddon = new FitAddon();
    let attachAddon; 
    term.loadAddon(fitAddon);

    // Function to re-fit terminal if its component's size changed
    function sizeChanged() {
      console.log("Resized!");
      fitAddon.fit();
    }
    sizeChanged();
    window.addEventListener("resize", sizeChanged);

    // To protect against race condition where we clean up before getting the websocket
    let disposed = false;

    async function attachSocket() {
      // Find the port to use from the server
      const res = await fetch("/api/websocket");
      const data = await res.json();
      const port = data.port;

      if (!disposed) {
        console.log("Trying to connect");
        // setSock(new WebSocket(`ws://localhost:${port}`))
        const sock = new WebSocket(`ws://localhost:${port}`);
        attachAddon = new AttachAddon(sock);

        term.loadAddon(attachAddon);
        term.open(termDiv.current);
      }
    }

    attachSocket();

    return () => {
      disposed = true;
      window.removeEventListener("resize", sizeChanged);
      fitAddon.dispose();
      if (attachAddon !== undefined) {
        attachAddon.dispose();
        term.dispose();
      }
    };
  }, [termDiv]);

  return <div id="terminal" ref={termDiv}></div>;
}
