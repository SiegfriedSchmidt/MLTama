import {io, Socket} from "socket.io-client";

export interface ServerToClientEvents {
  opponentMove: (data: { move: string, fen: string }) => void
}

export interface ClientToServerEvents {
  clientMove: (data: { move: string }, callback: (data: {status: string, content: string}) => void) => void
}

export const socket: Socket<ServerToClientEvents, ClientToServerEvents> = io('https://192.168.2.201:5000', {
  autoConnect: true, // Just to know that this option exists :)
});

