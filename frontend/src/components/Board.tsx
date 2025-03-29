import React, {CanvasHTMLAttributes, FC, useEffect, useRef, useState} from 'react';
import {Tama} from "@/utils/Graphics/tama.ts";
import {Box} from "@chakra-ui/react";

interface Props {
  FEN: string
}

const Board: FC<Props> = ({FEN}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    if (canvasRef.current) {
      const tama = new Tama(canvasRef.current, FEN)
      tama.drawBoard()
    }
  }, [canvasRef]);

  return (
    <Box width="min(85vw, 85vh)" height="auto">
      <canvas ref={canvasRef}/>
    </Box>
  );
};

export default Board;