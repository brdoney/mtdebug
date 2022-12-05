import "./ThreadPicker.css";

import useSWR from "swr";
import React from "react";
import { fetcher } from "./common";

export default function ThreadPicker({ thread, setThread, ...args }) {
  const { data: threads, error } = useSWR("/api/threads", fetcher);

  if (error) {
    return <p>Could not connect to api</p>;
  }

  let options = [
    <option key="-1" disabled value="default">
      Select a thread
    </option>,
  ];

  let variables = [];

  const haveThreads = threads && Object.keys(threads).length > 0;
  if (haveThreads) {
    options = options.concat(
      Object.entries(threads).map(([id, t]) => (
        <option key={id} value={id}>
          {id} {t["target-id"]}
        </option>
      ))
    );
    if (thread != null) {
      variables = threads[thread]["vars"].map((v) => (
        <tr key={v.name}>
          <td>{v.type}</td>
          <td>{v.name}</td>
          <td>{v.value}</td>
        </tr>
      ));
    }
  }

  const table = (
    <table>
      <thead>
        <tr>
          <th data-prop-name="type">Type</th>
          <th data-prop-name="name">Name</th>
          <th data-prop-name="value">Value</th>
        </tr>
      </thead>
      <tbody>{variables}</tbody>
    </table>
  );

  const handleChange = (e) => {
    const tid = e.target.value;
    setThread(tid);
  };

  return (
    <div class="thread-picker">
      <select
        disabled={!haveThreads}
        name="thread"
        id="thread"
        defaultValue="default"
        {...args}
        onChange={handleChange}
      >
        {options}
      </select>
      {variables.length > 0 ? table : ""}
    </div>
  );
}
