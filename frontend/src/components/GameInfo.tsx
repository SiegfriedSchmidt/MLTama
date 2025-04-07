import React, {FC} from 'react';
import {Box, DataList, Flex, Status, Text} from "@chakra-ui/react";
import {callbackInfoType} from "@/types/game.ts";

interface Props {
  info: callbackInfoType;
  currentSide: number;
}

const GameInfo: FC<Props> = ({info, currentSide}) => {
  return (
    <Box m={4}>
      <DataList.Root orientation="vertical">
        <Flex flexDirection="row" alignItems="center">
          <Text>{info.side == 1 ? 'White' : 'Black'}</Text>
          {currentSide == info.side ?
            <Status.Root ml={3} colorPalette="green">
              <Status.Indicator/>
            </Status.Root> : <></>
          }
        </Flex>
        <DataList.Item>
          <DataList.ItemLabel>Depth</DataList.ItemLabel>
          <DataList.ItemValue>{info?.depth}</DataList.ItemValue>
          <DataList.ItemLabel>Value</DataList.ItemLabel>
          <DataList.ItemValue>{info?.value}</DataList.ItemValue>
          {info?.victoryIn ?
            <>
              <DataList.ItemLabel>Victory in</DataList.ItemLabel>
              <DataList.ItemValue>{info.victoryIn} moves</DataList.ItemValue>
            </>
            : <></>}
        </DataList.Item>
      </DataList.Root>
    </Box>
  );
};

export default GameInfo;