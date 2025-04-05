import React, {FC} from 'react';
import {Box, DataList, Text} from "@chakra-ui/react";
import {callbackInfoType} from "@/types/game.ts";

interface Props {
  info: callbackInfoType;
}

const GameInfo: FC<Props> = ({info}) => {
  return (
    <Box m={4}>
      <DataList.Root orientation="vertical">
        <Text>{info.side == 1 ? 'White' : 'Black'}</Text>
        <DataList.Item>
          <DataList.ItemLabel>Depth</DataList.ItemLabel>
          <DataList.ItemValue>{info?.depth}</DataList.ItemValue>
          <DataList.ItemLabel>Value</DataList.ItemLabel>
          <DataList.ItemValue>{info?.value}</DataList.ItemValue>
          {info?.victoryIn ?
            <>
              <DataList.ItemLabel>Depth</DataList.ItemLabel>
              <DataList.ItemValue>{info.victoryIn}</DataList.ItemValue>
            </>
            : <></>}
        </DataList.Item>
      </DataList.Root>
    </Box>
  );
};

export default GameInfo;