import {io, Socket} from "socket.io-client";
import {pieceType} from "@/utils/Tama/pieceImg.ts";

export type ServerStatus = 'success' | 'error'
export type startGameParams = { room: string, fen: string, restart: boolean }

type callbackBase = { status: ServerStatus }

export interface ServerToClientEvents {
  select: (data: { piece: pieceType, select: [number, number], highlight: [number, number][] }) => void
  move: (data: { piece: pieceType, move: [number, number, number, number], fenStart: string, fenEnd: string }) => void
  start: (data: { room: string, fen: string }) => void
}

export interface ClientToServerEvents {
  start: (data: startGameParams, callback: (data: callbackBase) => void) => void
  click: (data: [number, number]) => void
}

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io('https://192.168.2.200:5000', {
  autoConnect: true, // Just to know that this option exists :)
});

