import {socket} from "../socket.ts";
import {useEffect, useState} from "react";

export default function useSocket() {
  const [opponentMove, setOpponentMove] = useState<{ move: string, fen: string }>();

  function clientMakeMove(move: string, callback: (data: { status: string, content: string }) => void) {
    socket.emit('clientMove', {move}, callback)
  }

  useEffect(() => {
    socket.on('opponentMove', (data) => {
      setOpponentMove(data);
    });

    return () => {
      socket.off('opponentMove');
    };
  }, []);

  return {clientMakeMove, opponentMove}
}