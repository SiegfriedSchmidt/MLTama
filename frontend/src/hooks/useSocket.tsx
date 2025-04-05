import {socket} from "../socket.ts";
import {useEffect, useState} from "react";

export default function useSocket() {
  const [info, setInfo] = useState<{ depth: number }>({depth: 0});
  const [win, setWin] = useState<{ winner: number }>();

  useEffect(() => {
    socket.on('info', setInfo);
    socket.on('win', setWin)

    return () => {
      socket.off('info');
      socket.off('win')
    };
  }, []);

  return {info, win}
}