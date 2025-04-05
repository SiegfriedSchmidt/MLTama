export type gameInfoType = { room: string }
export type startGameParams = { room: string, fen: string, restart: boolean }
export type callbackInfoType = { side: number, depth: number, value: number, victoryIn: number }