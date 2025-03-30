import {io, Socket} from "socket.io-client";
import {pieceType} from "@/utils/Tama/pieceImg.ts";

export type ServerStatus = 'success' | 'error'

type callbackBase = { status: ServerStatus }

export interface ServerToClientEvents {
  select: (data: { piece: pieceType, select: [number, number], highlight: [number, number][] }) => void
  move: (data: { piece: pieceType, move: [number, number, number, number], fenStart: string, fenEnd: string }) => void
}

export interface ClientToServerEvents {
  start: (
    data: string,
    callback: (data: callbackBase & { room: string, fen: string }) => void
  ) => void
  click: (data: [number, number]) => void
}

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io('https://192.168.2.201:5000', {
  autoConnect: true, // Just to know that this option exists :)
});

