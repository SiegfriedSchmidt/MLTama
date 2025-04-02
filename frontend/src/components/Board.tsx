import React, {MouseEvent, FC, useEffect, useRef, Ref, useImperativeHandle} from 'react';
import {TamaBoard} from "@/utils/Tama/tamaBoard.ts";
import {Box} from "@chakra-ui/react";
import {gameInfoType} from "@/types/game.ts";
import {startGameParams} from "@/socket.ts";

interface Props {
  ref: Ref<(data: startGameParams) => void>
  onGameInfo: (data: gameInfoType) => void
}

const Board: FC<Props> = ({onGameInfo, ref}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const tamaBoardRef = useRef<TamaBoard | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      tamaBoardRef.current = new TamaBoard(canvasRef.current)
      tamaBoardRef.current.registerEvents()
    }

    return () => {
      if (tamaBoardRef.current) tamaBoardRef.current.endGame()
    }
  }, [canvasRef]);

  useImperativeHandle(ref, () => {
    return (data) => tamaBoardRef.current?.startGame(data)
  }, [tamaBoardRef])

  useEffect(() => {
    if (tamaBoardRef.current) {
      tamaBoardRef.current.onGameInfo = onGameInfo
    }
  }, [tamaBoardRef, onGameInfo]);

  function handleBoardClick(event: MouseEvent) {
    if (!tamaBoardRef.current) return

    tamaBoardRef.current.onClick(event.clientX, event.clientY)
  }

  return (
    <canvas ref={canvasRef} onMouseDown={handleBoardClick}/>
  );
};

export default Board;