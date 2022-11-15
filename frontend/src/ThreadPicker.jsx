import useSWR from "swr";
import React from "react";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function ThreadPicker({ ...args }) {
  const { data: threads, error } = useSWR("/api/threads", fetcher, {refreshInterval: 10});
  const [thread, this_thread] = React.useState();

  if (error) {
    return <p>Could not connect to api</p>;
  }

  let options = [
    <option key="-1" disabled value="default">
      Select a thread
    </option>,
  ];
  if (threads) {
    console.log(threads)
    options = options.concat(
      threads.map((t) => (
        <option key={t.id} value={t.id}>{`${t.id} ${t["target_id"]}`}</option>
      ))
    );
  }

  const handleChange = (e) =>
  {
    const val = e.target.value;
    this_thread(val);
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
      <p >{thread}</p>
      <p >Local vars:</p>
      <p >Global vars:</p>
      <p >Locks held:</p>
    </div>
  );
}
