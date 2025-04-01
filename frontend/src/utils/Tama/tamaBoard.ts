import {isCharNumber} from "@/utils/helpers.ts";
import {boardColor} from "@/styles/GlobalStyles.tsx";
import {isPiece, pieceImg, pieceType} from "@/utils/Tama/pieceImg.ts";
import {socket} from "@/socket.ts";

export class TamaBoard {
  private readonly ctx: CanvasRenderingContext2D;
  private fen = ''
  private gridSize = 8
  private lineWidth = 5
  private imagePad = 6
  private cellSize = 96
  private moveVelocity = 5
  private size = this.gridSize * (this.cellSize + this.lineWidth) + this.lineWidth

  private stopShaking = () => {
  }
  private moving = false;

  constructor(
    private readonly canvas: HTMLCanvasElement,
  ) {
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas graphics not supported!");

    this.ctx = context;

    this.canvas.style.width = '100%';
    this.canvas.style.height = 'auto';
    this.canvas.width = this.size
    this.canvas.height = this.size
  }

  startGame(room: string, onStart: (room: string) => void) {
    this.registerEvents()
    socket.emit('start', room, ({status, room, fen}) => {
      if (status === 'success') {
        this.fen = fen
        this.drawBoard()
        onStart(room)
      }
    })
  }

  endGame() {
    this.unregisterEvents()
  }

  private registerEvents() {
    socket.on('select', ({piece, select, highlight}) => {
      this.stopShaking()
      this.drawBoard()
      this.highlight(highlight)
      this.startShaking(piece, ...select)
    })

    socket.on('move', async ({piece, move, fenStart, fenEnd}) => {
      this.stopShaking()
      this.fen = fenStart
      await this.move(piece, ...move)
      this.fen = fenEnd
      console.log(this.fen)
      this.drawBoard()
    })
  }

  private unregisterEvents() {
    socket.off('select');
    socket.off('move')
  }

  private drawBoard() {
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

    for (const char of this.fen.split(' ')[0]) {
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

    if (!this.moving) {
      socket.emit('click', [row, col])
    }
  }

  highlight(cells: [number, number][]) {
    for (const [lightRow, lightCol] of cells) {
      this.drawCircle(lightRow, lightCol)
    }
  }

  startShaking(piece: pieceType, row: number, col: number) {
    const [x, y] = this.posToPixels(row, col)
    let shaking = true

    const shake = (startT: number, curT: number) => {
      const t = (curT - startT) / 16
      this.drawRect(row, col)
      this.ctx.drawImage(pieceImg[piece], x + this.imagePad + Math.sin(t / 10) * this.imagePad, y + this.imagePad + Math.cos(t / 4) * this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)
      if (shaking) {
        requestAnimationFrame((time) => startT ? shake(startT, time) : shake(time, time))
      } else {
        this.drawRect(row, col)
        this.drawPiece(row, col, piece)
      }
    }
    requestAnimationFrame((time) => shake(time, time))
    this.stopShaking = () => shaking = false
  }

  move(piece: pieceType, fromRow: number, fromCol: number, toRow: number, toCol: number) {
    return new Promise<void>((resolve, reject) => {
      if (fromRow == toRow && fromCol == toCol) return
      this.moving = true

      const [fromX, fromY] = this.posToPixels(fromRow, fromCol)
      const [toX, toY] = this.posToPixels(toRow, toCol)

      const [vx, vy] = [toX - fromX, toY - fromY]
      const len = Math.sqrt(vx * vx + vy * vy)
      const dirX = vx / len
      const dirY = vy / len

      const move = (startT: number, curT: number) => {
        const t = (curT - startT) / 16
        let x = dirX * this.moveVelocity * t + fromX
        let y = dirY * this.moveVelocity * t + fromY

        if ((dirX * (x - toX) >= 0) && (dirY * (y - toY) >= 0)) {
          x = toX
          y = toY
        }

        this.drawBoard()
        this.ctx.drawImage(pieceImg[piece], x + this.imagePad, y + this.imagePad, this.cellSize - this.imagePad * 2, this.cellSize - this.imagePad * 2)

        if (x == toX && y == toY) {
          resolve()
          this.moving = false
        } else {
          requestAnimationFrame((time) => startT ? move(startT, time) : move(time, time))
        }
      }
      requestAnimationFrame((time) => move(time, time))
    })
  }
}
