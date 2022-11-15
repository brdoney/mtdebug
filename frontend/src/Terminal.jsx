import "./Terminal.css";
import "../node_modules/xterm/css/xterm.css";
import { useEffect, useRef } from "react";
import { Terminal } from "xterm";
import { AttachAddon } from "xterm-addon-attach";
import { FitAddon } from "xterm-addon-fit";

export default function GDBTerminal() {
  const termDiv = useRef(null);
  // eslint-disable-next-line no-unused-vars
  // const [term, _setTerm] = useState(new Terminal());
  // // eslint-disable-next-line no-unused-vars
  // const [fitAddon, _setFitAddon] = useState(new FitAddon());
  // const [sock, setSock] = useState(null);

  // useEffect(() => {
  //   term.loadAddon(fitAddon);
  // }, [term, fitAddon]);

  // useLayoutEffect(() => {
  //   // NOTE: May lead to race condition when addon is loaded?
  //   function sizeChanged() {
  //     fitAddon.fit();
  //     if (sock !== null) {
  //       sock.
  //     }
  //   }
  //   window.addEventListener("resize", sizeChanged);
  //   sizeChanged();
  //   return () => window.removeEventListener("resize", sizeChanged);
  // }, [fitAddon]);

  useEffect(() => {
    const term = new Terminal()
    const fitAddon = new FitAddon();
    term.open(document.getElementById("terminal"));

    fitAddon.fit();

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
        const sock =new WebSocket(`ws://localhost:${port}`)
        const attachAddon = new AttachAddon(sock);

        term.loadAddon(attachAddon);
      }
    }

    attachSocket();

    return () => {
      disposed = true;
      term.dispose();
    };
  }, []);

  return <div id="terminal" ref={termDiv}></div>;
}
