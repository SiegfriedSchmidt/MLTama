import b from '../../assets/pieces/bman.png'
import B from '../../assets/pieces/bdamone.png'
import w from '../../assets/pieces/wman.png'
import W from '../../assets/pieces/wdamone.png'

export type pieceType = 'w' | 'W' | 'b' | 'B'

export function isPiece(piece: string): piece is pieceType {
  return ['w', 'W', 'b', 'B'].includes(piece)
}

export const pieceImg: { [key in pieceType]: HTMLImageElement } = {
  b: new Image(),
  B: new Image(),
  w: new Image(),
  W: new Image()
}

pieceImg.b.src = b
pieceImg.B.src = B
pieceImg.w.src = w
pieceImg.W.src = W