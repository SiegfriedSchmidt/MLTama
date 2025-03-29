import {createGlobalStyle} from "styled-components";

const GlobalStyles = createGlobalStyle`
    #root {
        width: 100vw;
        height: 100vh;
    }

    //@media all and (display-mode: standalone) {
    //    body {
    //        margin-top: 50px;
    //    }
    //}
`

export const boardColor = 'rgb(168,92,92)'

export default GlobalStyles