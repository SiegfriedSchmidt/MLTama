import React, {} from 'react';
import {Box, Flex} from "@chakra-ui/react";
import {ColorModeButton} from "@/components/ui/color-mode.tsx";
import {Toaster} from "@/components/ui/toaster"

const Header = () => {
  return (
    <Box position="absolute" m={4}>
      <ColorModeButton alignSelf="start"/>
      <Toaster/>
    </Box>
  );
};

export default Header;