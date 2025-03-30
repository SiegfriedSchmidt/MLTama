import React, {useEffect} from 'react';
import {Text, Flex} from "@chakra-ui/react";
import useSocket from "@/hooks/useSocket.tsx";
import Board from "@/components/Board.tsx";

const HomePage = () => {
  return (
    <Flex height="100%" justifyContent="center" alignItems="center">
      <Board/>
    </Flex>
  );
};

export default HomePage;