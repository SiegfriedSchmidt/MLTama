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

  public selected: [number, number] | null = null

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

  posToPixels(row: number, col: number): [number, number] {
    return [
      col * (this.cellSize + this.lineWidth) + this.lineWidth,
      row * (this.cellSize + this.lineWidth) + this.lineWidth
    ]
  }

  pixelsToPos(x: number, y: number): [number, number] {
    return [
      Math.floor((y - this.lineWidth / 2) / (this.cellSize + this.lineWidth)),
      Math.floor((x - this.lineWidth / 2) / (this.cellSize + this.lineWidth))
    ]
  }

  drawPiece(row: number, col: number, char: pieceType) {
    const [x, y] = this.posToPixels(row, col)
    this.ctx.drawImage(pieceImg[char], x + this.imagePad, y + this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)
  }

  drawRect(row: number, col: number) {
    this.ctx.fillStyle = boardColor
    this.ctx.fillRect(...this.posToPixels(row, col), this.cellSize, this.cellSize)
  }

  drawCircle(row: number, col: number) {
    this.ctx.fillStyle = 'rgb(0, 150, 0)'
    this.ctx.beginPath();

    const [x, y] = this.posToPixels(row, col)
    const r = this.cellSize / 3
    this.ctx.arc(x + this.cellSize / 2, y + +this.cellSize / 2, r, 0, 2 * Math.PI)
    this.ctx.fill()

    this.ctx.lineWidth = this.lineWidth / 2
    this.ctx.stroke();
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

  public onClick(eventX: number, eventY: number) {
    const rect = this.canvas.getBoundingClientRect();
    const scaleX = this.canvas.width / rect.width;
    const scaleY = this.canvas.height / rect.height;

    const [row, col] = this.pixelsToPos((eventX - rect.left) * scaleX, (eventY - rect.top) * scaleY)

    if (this.selected) {
      this.move(...this.selected, row, col)
      this.selected = null
      return
    }

    this.selected = [row, col]
    this.startShaking(row, col)
  }

  startShaking(row: number, col: number) {
    const [x, y] = this.posToPixels(row, col)
    this.drawCircle(row - 1, col - 1)
    this.drawCircle(row - 1, col)
    this.drawCircle(row - 1, col + 1)
    const shake = (t: number) => {
      this.drawRect(row, col)
      this.ctx.drawImage(pieceImg['w'], x + this.imagePad + Math.sin(t / 10) * this.imagePad, y + this.imagePad + Math.cos(t / 4) * this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)
      if (this.selected) requestAnimationFrame(() => shake(t + 1))
    }
    shake(0)
  }

  move(fromRow: number, fromCol: number, toRow: number, toCol: number) {
    const [fromX, fromY] = this.posToPixels(fromRow, fromCol)
    const [toX, toY] = this.posToPixels(toRow, toCol)

    const move = (t: number) => {
      const step = t * 2
      const x = (toX - fromX) / 100 * step + fromX
      const y = (toY - fromY) / 100 * step + fromY
      this.drawBoard()
      this.ctx.drawImage(pieceImg['w'], x + this.imagePad, y + this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)

      if (step < 100) requestAnimationFrame(() => move(t + 1))
    }

    move(0)
  }
}
