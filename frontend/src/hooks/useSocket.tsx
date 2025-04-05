import {socket} from "../socket.ts";
import {useEffect, useState} from "react";

export default function useSocket() {
  const [info, setInfo] = useState<{ depth: number }>({depth: 0});

  useEffect(() => {
    socket.on('info', (data) => {
      setInfo(data);
    });

    return () => {
      socket.off('info');
    };
  }, []);

  return {info}
}