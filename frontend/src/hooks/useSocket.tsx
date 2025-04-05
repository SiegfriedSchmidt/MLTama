import {socket} from "../socket.ts";
import {useEffect, useState} from "react";
import {callbackInfoType} from "@/types/game.ts";

export default function useSocket() {
  const [info, setInfo] = useState<{ white: callbackInfoType, black: callbackInfoType, both: { depth: number } }>({
    white: {side: 0, depth: 0, value: 0, victoryIn: 0},
    black: {side: 0, depth: 0, value: 0, victoryIn: 0},
    both: {depth: 0}
  });
  const [win, setWin] = useState<{ winner: number }>();

  useEffect(() => {
    socket.on('info', (data) => {
      if (data.side == 1) {
        setInfo(info => {
          return {...info, white: data, both: data}
        })
      } else {
        setInfo(info => {
          return {...info, black: data, both: data}
        })
      }
    });
    socket.on('win', setWin)

    return () => {
      socket.off('info');
      socket.off('win')
    };
  }, []);

  return {info, win}
}