import { createGlobalStyle, styled } from "styled-components";

export const Wrapper = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    z-index: 9999;
`;

export const Box = styled.div`
    background-color: ${(props) =>
        props.theme.bg === "auto" ? "inherit" : props.theme.bg};
    color: ${(props) =>
        props.theme.accent === "auto" ? "inherit" : props.theme.accent};
    width: 33vw;
    height: 33vh;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
    z-index: 10000;
`;

export const BaseButton = styled.button`
    background-color: ${(props) =>
        props.theme.accent === "auto" ? "#00a4cc" : props.theme.accent};
    color: ${(props) => {
        if (props.theme.bg === "auto") return "white";
        return props.theme.bg;
    }};
    border: none;
    padding: ${(props) => (props.small ? "5px 10px" : "10px 20px")};
    margin: ${(props) => (props.small ? "5px" : "10px 0")};
    border-radius: 5px;
    cursor: pointer;

    &:hover {
        opacity: 0.8;
    }
`;

export const Button = styled(BaseButton)`
    margin-top: 10px;
`;

export const GlobalStyles = createGlobalStyle`
    html, body {
        margin: 0;
        padding: 0;
        overflow: hidden;
    }

    body {
        -ms-overflow-style: none;  /* IE и Edge */
        scrollbar-width: none;     /* Firefox */
    }

    body::-webkit-scrollbar {
        display: none;             /* Chrome, Safari и Opera */
    }
`;
