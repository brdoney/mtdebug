import { useSWRConfig } from "swr";

export const fetcher = (...args) => fetch(...args).then((res) => res.json());

export function useWriteGdb(selectedThreadId) {
  const { mutate } = useSWRConfig();

  const invalidateCache = () => {
    mutate("/api/resources");
    mutate("/api/threads");
    if (selectedThreadId !== undefined) {
      mutate(`/api/step/${selectedThreadId}`);
    }
  };

  const post = async (url) => {
    // We have to wait for post to be done before checking for updated data b/c
    // browser messes up queueing? So this is just to be safe
    await fetch(url, { method: "POST" });
    invalidateCache();
  };

  const postJson = async (url, json) => {
    // Await is for same reason as normal post
    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(json),
    });
    invalidateCache();
  };

  return { post, postJson };
}
