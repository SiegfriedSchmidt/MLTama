import React, {useEffect} from 'react';
import {Text, Flex} from "@chakra-ui/react";
import useSocket from "@/hooks/useSocket.tsx";
import Board from "@/components/Board.tsx";

const HomePage = () => {
  return (
    <Flex height="100%" justifyContent="center" alignItems="center">
      <Board FEN={'8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w'}/>
    </Flex>
  );
};

export default HomePage;