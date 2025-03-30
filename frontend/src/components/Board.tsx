import React, {CanvasHTMLAttributes, MouseEvent, FC, useEffect, useRef, useState} from 'react';
import {Tama} from "@/utils/Graphics/tama.ts";
import {Box} from "@chakra-ui/react";

const Board: FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const tamaRef = useRef<Tama | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      const tama = new Tama(canvasRef.current, '8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
      tamaRef.current = tama
      tama.drawBoard()
    }
  }, [canvasRef]);

  function handleBoardClick(event: MouseEvent) {
    if (!canvasRef.current || !tamaRef.current) return

    tamaRef.current.onClick(event.clientX, event.clientY)
  }

  return (
    <Box width="min(85vw, 85vh)" height="auto">
      <canvas ref={canvasRef} onMouseDown={handleBoardClick}/>
    </Box>
  );
};

export default Board;