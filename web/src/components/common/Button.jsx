import styled, { css } from 'styled-components';

const Button = styled.button`
  // Базовые стили
  padding: ${props => props.$small ? '8px 16px' : '12px 24px'};
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: ${props => props.$small ? '14px' : '16px'};
  font-weight: 500;
  transition: all 0.2s ease;
  
  // Позиционирование
  ${props => props.$position && css`
    position: ${props.$fixed ? 'fixed' : 'absolute'};
    ${props.$position.top !== undefined && `top: ${props.$position.top}px`};
    ${props.$position.right !== undefined && `right: ${props.$position.right}px`};
    ${props.$position.bottom !== undefined && `bottom: ${props.$position.bottom}px`};
    ${props.$position.left !== undefined && `left: ${props.$position.left}px`};
    z-index: ${props.$zIndex || 1000};
  `}

  // Цвета
  background-color: ${props => props.$variant === 'outlined' 
    ? 'transparent' 
    : props.theme.accent};
  color: ${props => props.$variant === 'outlined' 
    ? props.theme.accent 
    : props.theme.bg};
  border: ${props => props.$variant === 'outlined' 
    ? `2px solid ${props.theme.accent}` 
    : 'none'};

  // Состояния
  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
    background-color: ${props => props.$variant === 'outlined' 
      ? props.theme.accent + '20'
      : props.theme.accent};
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  ${props => props.$fullWidth && css`
    width: 100%;
  `}
`;

export default Button;