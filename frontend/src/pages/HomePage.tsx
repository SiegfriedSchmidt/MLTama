import React, {useEffect, useState} from 'react';
import {Text, Flex} from "@chakra-ui/react";
import useSocket from "@/hooks/useSocket.tsx";
import Board from "@/components/Board.tsx";

const HomePage = () => {
  const [room, setRoom] = useState<string>('1000')

  return (
    <Flex height="100%" justifyContent="center" alignItems="center" direction="column">
      <Text>{room}</Text>
      <Board room={room} setRoom={setRoom}/>
    </Flex>
  );
};

export default HomePage;