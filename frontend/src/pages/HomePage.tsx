import React, {useEffect, useRef, useState} from 'react';
import {Text, Flex, Box, Button} from "@chakra-ui/react";
import Board from "@/components/Board.tsx";
import {gameInfoType, startGameParams} from "@/types/game.ts";

const HomePage = () => {
  const [gameInfo, setGameInfo] = useState<gameInfoType>()
  const startGameRef = useRef<(data: startGameParams) => void>(null);

  useEffect(() => {
    startGameRef.current?.({room: '1000', fen: '', restart: false})
  }, [startGameRef]);

  function onClick() {
    startGameRef.current?.({room: '1000', fen: '', restart: true})
  }

  return (
    <>
      <Box width="min(85vw, 85vh)" height="auto" position='absolute' margin='auto' left={0} right={0} top={0}>
        <Flex flexDirection="row" justifyContent="center" alignItems="center">
          <Text m={2}>Room id: {gameInfo?.room}</Text>
          <Button m={2} onClick={onClick}>Restart game</Button>
        </Flex>

        <Board ref={startGameRef} onGameInfo={setGameInfo}/>
      </Box>
    </>
  );
};

export default HomePage;