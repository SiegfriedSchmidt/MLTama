import {io, Socket} from "socket.io-client";

export type ServerStatus = 'success' | 'error'

type callbackBase = { status: ServerStatus }

export interface ServerToClientEvents {
  select: (data: { select: [number, number], highlight: [number, number][] }) => void
  move: (data: { move: [number, number, number, number], fenStart: string, fenEnd: string }) => void
}

export interface ClientToServerEvents {
  start: (
    data: string,
    callback: (data: callbackBase & { room: string, fen: string }) => void
  ) => void
  click: (data: [number, number]) => void
}

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io('https://192.168.2.200:5000', {
  autoConnect: true, // Just to know that this option exists :)
});

