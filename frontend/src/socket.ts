import {io, Socket} from "socket.io-client";
import {pieceType} from "@/utils/Tama/pieceImg.ts";
import {callbackInfoType, startGameParams} from "@/types/game.ts";

export type ServerStatus = 'success' | 'warning' | 'error'

type callbackBase = { status: ServerStatus }

export interface ServerToClientEvents {
  select: (data: { piece: pieceType, select: [number, number], highlight: [number, number][] }) => void
  move: (data: [{ piece: pieceType, move: [number, number, number, number], fenStart: string, fenEnd: string }]) => void
  info: (data: callbackInfoType) => void
  win: (data: { winner: number }) => void
  start: (data: { room: string, fen: string }) => void
}

export interface ClientToServerEvents {
  start: (data: startGameParams, callback: (data: callbackBase) => void) => void
  click: (data: [number, number]) => void
}

const url = process.env.NODE_ENV === 'production' ? '/' : 'https://192.168.2.200:5000'
export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io(url, {
  autoConnect: true, // Just to know that this option exists :)
});

