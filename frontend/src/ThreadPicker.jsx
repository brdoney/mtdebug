import useSWR from "swr";
import React from "react";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function ThreadPicker({ ...args }) {
  const { data: threads, error } = useSWR("/api/threads", fetcher, {refreshInterval: 10});
  const [thread, setThread] = React.useState();

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
        <option key={t.tid} value={t.tid}>{`${t.tid} ${t["target-id"]}`}</option>
      ))
    );
    for(var i = 0; i < threads.length; i++)
    {
      if(threads[i]["vars"])
      {
        let curr = []; 
        curr = curr.concat(
          threads[i]["vars"].map((v) => (
            <p>{`${v.name} ${v.value}`}</p>
          ))
        );
        variables.push(curr)
      }
    }
  }

  console.log(threads)

  const handleChange = (e) =>
  {
    const tid = e.target.value;
    setThread(variables[tid-1]);
  };

  return (
    <div>
      <select
        disabled={!threads || threads.length === 0}
        name="thread"
        id="thread"
        defaultValue="default"
        {...args}
      onChange={handleChange}>

        {options}
      </select>
      <div >Local vars: {thread}</div>
      <p >Global vars:</p>
      <p >Locks held:</p>
    </div>
  );
}
