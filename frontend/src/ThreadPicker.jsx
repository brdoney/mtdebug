import useSWR from "swr";

const fetcher = (...args) => fetch(...args).then((res) => res.json());

export default function ThreadPicker({ ...args }) {
  const { data: threads, error } = useSWR("/api/threads", fetcher);

  if (error) {
    return <p>Could not connect to api</p>;
  }

  let options = [
    <option key="-1" disabled value="default">
      Select a thread
    </option>,
  ];
  if (threads) {
    options = options.concat(
      threads.map((t) => (
        <option key={t.id} value={t.id}>{`${t.id} ${t["target-id"]}`}</option>
      ))
    );
  }

  return (
    <select
      disabled={!threads || threads.length === 0}
      name="thread"
      id="thread"
      defaultValue="default"
      {...args}
    >
      {options}
    </select>
  );
}
