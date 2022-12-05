import "./MutexView.css";

import useSWR from "swr";
import { fetcher } from "./common";

export default function MutexView() {
  const { data: resources, error: resourceError } = useSWR(
    "/api/resources",
    fetcher
  );
  const { data: threads, error: threadsError } = useSWR(
    "/api/threads",
    fetcher
  );

  if (resourceError) {
    return <p>Couldn't fetch resource state</p>;
  } else if (threadsError) {
    return <p>Couldn't construct thread translations</p>;
  } else if (!resources) {
    return <p>Fetching resource state</p>;
  } else if (!threads) {
    return <p>Constructing thread translations</p>;
  } else if (Object.keys(resources).length === 0) {
    return <p>No resources yet</p>;
  }

  const threadMap = {};
  const re = new RegExp("Thread (0[xX][0-9a-fA-F]+)");
  for (const thread of threads) {
    const tidString = thread["target-id"];
    const match = re.exec(tidString);
    const tidHex = match[1];
    const tid = parseInt(tidHex, 16);
    threadMap[tid] = { id: thread.id, "target-id": tidString };
  }

  let resourceEntries = [];
  // eslint-disable-next-line no-unused-vars
  for (const [_address, rs] of Object.entries(resources)) {
    let waiters;
    if (Object.keys(rs.waiters).length > 0) {
      const waiterEls = rs.waiters.map((waiter) => (
        <li>
          {threadMap[waiter].id} {threadMap[waiter]["target-id"]}
        </li>
      ));
      waiters = <ul>{waiterEls}</ul>;
    } else {
      waiters = "No one is waiting on this mutex";
    }

    const owner = threadMap[rs.owner];
    const entry = (
      <li>
        <p>
          Owner: {owner.id} {owner["target-id"]}
          <br />
          Waiters: {waiters}
        </p>
      </li>
    );
    resourceEntries.push(entry);
  }

  return (
    <div>
      <h3>Mutexes</h3>
      <ul className="resources">{resourceEntries}</ul>
    </div>
  );
}
