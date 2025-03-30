import React, {MouseEvent, FC, useEffect, useRef, useState} from 'react';
import {TamaBoard} from "@/utils/Tama/tamaBoard.ts";
import {Box} from "@chakra-ui/react";

interface Props {
  setRoom: (room: string) => void
  room: string
}

const Board: FC<Props> = ({room, setRoom}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const tamaBoardRef = useRef<TamaBoard | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      tamaBoardRef.current = new TamaBoard(canvasRef.current)
      tamaBoardRef.current.startGame(room, setRoom)
    }

    return () => {
      if (tamaBoardRef.current) tamaBoardRef.current.endGame()
    }
  }, [canvasRef, setRoom]);

  function handleBoardClick(event: MouseEvent) {
    if (!tamaBoardRef.current) return

    tamaBoardRef.current.onClick(event.clientX, event.clientY)
  }

  return (
    <Box width="min(85vw, 85vh)" height="auto">
      <canvas ref={canvasRef} onMouseDown={handleBoardClick}/>
    </Box>
  );
};

export default Board;