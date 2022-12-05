import useSWR from "swr";
import React from "react";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

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

  let variables = [
  ];

  if (threads) {
    options = options.concat(
      threads.map((t) => (
        <option key={t.id} value={t.id}>{`${t.id} ${t["target-id"]}`}</option>
      ))
    );
    for(var i = 0; i < threads.length; i++)
    {
      if(threads[i]["vars"])
      {
        let curr = [];
        curr = curr.concat(threads[i]["vars"].map((v) => (
          <tr><td>{`${v.type}`}</td><td>{`${v.name}`}</td> <td>{`${v.value}`}</td></tr>
        )))
        variables.push(curr)
      }
    }
  }

  const handleChange = (e) =>
  {
    const tid = e.target.value;
    setThread(variables[tid-1]);
  };

  return (
    <body>
      <div id="threadPicker">
        <select
          disabled={!threads || threads.length === 0}
          name="thread"
          id="thread"
          defaultValue="default"
          {...args}
        onChange={handleChange}>

          {options}
        </select>
        <table>
          <thead>
            <tr>
              <th data-prop-name='type'>Type</th>
              <th data-prop-name='name'>Name</th>
              <th data-prop-name='value'>Value</th>
            </tr>
          </thead>
          {thread}
        </table>
      </div>
    </body>
  );
}
