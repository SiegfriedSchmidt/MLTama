import React, {} from 'react';
import {Flex} from "@chakra-ui/react";
import {ColorModeButton} from "@/components/ui/color-mode.tsx";
import {Toaster} from "@/components/ui/toaster"

const Header = () => {
  return (
    <Flex justifyContent="space-between" padding="20px" paddingRight="50px">
      <ColorModeButton alignSelf="start"/>
      <Toaster/>
    </Flex>
  );
};

export default Header;