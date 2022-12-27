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
  for (const [gdbId, thread] of Object.entries(threads)) {
    const tidString = thread["target-id"];
    const match = re.exec(tidString);
    const tidHex = match[1];
    const tid = parseInt(tidHex, 16);
    threadMap[tid] = { id: gdbId, "target-id": tidString };
  }

  let resourceEntries = [];
  // eslint-disable-next-line no-unused-vars
  for (const [address, rs] of Object.entries(resources)) {
    let waiters;
    if (Object.keys(rs.waiters).length > 0) {
      const waiterEls = rs.waiters.map((waiter) => (
        <li key={waiter}>
          {threadMap[waiter].id} {threadMap[waiter]["target-id"]}
        </li>
      ));
      waiters = <ul>{waiterEls}</ul>;
    } else {
      waiters = "No one is waiting on this mutex";
    }

    let owner = <p>Owner: No owner</p>;
    if (rs.owner != null) {
      const ownerInfo = threadMap[rs.owner];
      owner = (
        <p>
          Owner: {ownerInfo.id} {ownerInfo["target-id"]}
        </p>
      );
    }
    const entry = (
      <div className="resource-entry" key={address}>
        {owner}
        <p>Waiters: </p>
        <div className="resource-waiters">{waiters}</div>
      </div>
    );
    resourceEntries.push(entry);
  }

  return (
    <div>
      <h3>Mutexes</h3>
      <div className="resources">{resourceEntries}</div>
    </div>
  );
}
