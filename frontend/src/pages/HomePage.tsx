import React, {useEffect} from 'react';
import {Text, Flex} from "@chakra-ui/react";
import useSocket from "@/hooks/useSocket.tsx";

const HomePage = () => {
  return (
    <Flex height="100%" justifyContent="center" alignItems="center">
      <Text textStyle="5xl">Machine Learning Tama</Text>
    </Flex>
  );
};

export default HomePage;