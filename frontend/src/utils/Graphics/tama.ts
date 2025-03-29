import {isCharNumber} from "@/utils/helpers.ts";
import {boardColor} from "@/styles/GlobalStyles.tsx";
import {isPiece, pieceImg, pieceType} from "@/utils/pieceImg.ts";

export class Tama {
  private readonly ctx: CanvasRenderingContext2D;
  private gridSize = 8
  private lineWidth = 5
  private imagePad = 6
  private cellSize = 96
  private size = this.gridSize * (this.cellSize + this.lineWidth) + this.lineWidth

  constructor(
    private readonly canvas: HTMLCanvasElement,
    private FEN: string
  ) {
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas graphics not supported!");

    this.ctx = context;

    this.canvas.style.width = '100%';
    this.canvas.style.height = 'auto';
    this.canvas.width = this.size
    this.canvas.height = this.size
  }

  drawBoard() {
    this.ctx.fillStyle = boardColor
    this.ctx.fillRect(this.lineWidth / 2, this.lineWidth / 2, this.size - this.lineWidth, this.size - this.lineWidth);

    this.ctx.strokeStyle = 'black'
    this.ctx.lineWidth = this.lineWidth
    this.ctx.beginPath();
    this.ctx.roundRect(this.lineWidth / 2, this.lineWidth / 2, this.size - this.lineWidth, this.size - this.lineWidth, [4]);

    // grid
    for (let x = this.cellSize + this.lineWidth * 1.5; x < this.size; x += this.cellSize + this.lineWidth) {
      this.ctx.moveTo(x, this.lineWidth);
      this.ctx.lineTo(x, this.size - this.lineWidth);
      this.ctx.moveTo(this.lineWidth, x);
      this.ctx.lineTo(this.size - this.lineWidth, x);
    }

    this.ctx.stroke();
    this.drawPieces()
  }

  posToPixels(row: number, col: number): { x: number; y: number } {
    return {
      x: col * (this.cellSize + this.lineWidth) + this.lineWidth,
      y: row * (this.cellSize + this.lineWidth) + this.lineWidth
    };
  }

  drawPiece(row: number, col: number, char: pieceType) {
    const {x, y} = this.posToPixels(row, col)
    this.ctx.drawImage(pieceImg[char], x + this.imagePad, y + this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)
  }

  drawPieces() {
    let row = 7;
    let col = 0;

    this.ctx.fillStyle = 'blue'

    for (const char of this.FEN.split(' ')[0]) {
      if (char === '/') {
        --row
        col = 0
      } else {
        if (isCharNumber(char)) {
          col += Number(char)
          continue
        }

        if (!isPiece(char)) {
          throw new Error(`Invalid char piece: ${char}`)
        }

        this.drawPiece(row, col, char)
        ++col
      }
    }
  }
}
