import styled, { keyframes, css } from 'styled-components';

/* ============================================================
   BOOKMARK BRAND — Styled Components
   Dynamic, interactive brand elements: splatters, brush borders
   ============================================================ */

// --- Brand Constants ---
export const BRAND = {
  black: '#0d0d0d',
  lime: '#4caf27',
  limeDark: '#3d8e1f',
  limeLight: '#5ecb38',
  coral: '#e8613a',
  yellow: '#f5c842',
  bgWarm: '#f9f8f3',
  white: '#ffffff',
  textMuted: '#7a7a72',
  borderLight: '#e5e3db',
};

// --- Animations ---
const popIn = keyframes`
  0% { transform: scale(0); opacity: 0; }
  60% { transform: scale(1.4); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
`;

const drift = keyframes`
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(2px, -3px); }
  50% { transform: translate(-1px, 2px); }
  75% { transform: translate(3px, 1px); }
`;

// --- Paint Splatter Dot ---
export const SplatterDot = styled.span`
  position: absolute;
  width: ${({ size }) => size || 12}px;
  height: ${({ size }) => size || 12}px;
  border-radius: 50%;
  background: ${({ color }) => color || BRAND.coral};
  top: ${({ top }) => top || 'auto'};
  left: ${({ left }) => left || 'auto'};
  right: ${({ right }) => right || 'auto'};
  bottom: ${({ bottom }) => bottom || 'auto'};
  animation: ${popIn} 0.5s ease-out ${({ delay }) => delay || '0s'} both;
  pointer-events: none;
  z-index: 1;

  ${({ $animate }) =>
    $animate &&
    css`
      animation: ${popIn} 0.5s ease-out ${({ delay }) => delay || '0s'} both,
                 ${drift} 4s ease-in-out infinite;
    `}
`;

// --- Rough Circle (Logo Background) ---
export const RoughCircle = styled.div`
  width: ${({ size }) => size || 220}px;
  height: ${({ size }) => size || 220}px;
  border-radius: 50%;
  border: 4px solid ${BRAND.lime};
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;

  /* Rough, hand-drawn effect via box-shadow layering */
  box-shadow:
    inset 0 0 0 3px rgba(76, 175, 39, 0.15),
    0 0 0 2px rgba(76, 175, 39, 0.3),
    3px -2px 0 1px rgba(76, 175, 39, 0.2),
    -2px 3px 0 1px rgba(76, 175, 39, 0.15);

  &::before {
    content: '';
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 2px solid rgba(76, 175, 39, 0.25);
  }

  &::after {
    content: '';
    position: absolute;
    inset: -12px;
    border-radius: 50%;
    border: 1px solid rgba(76, 175, 39, 0.1);
  }
`;

// --- Brush Stroke Border ---
export const BrushStrokeBorder = styled.div`
  position: relative;
  border: 3px solid ${BRAND.lime};
  border-radius: 12px;

  /* Create an organic, hand-drawn border effect */
  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: 10px;
    right: 10px;
    height: 5px;
    background: ${BRAND.lime};
    border-radius: 2px;
  }
`;

// --- Card with Brush Top Border ---
export const BrushTopCard = styled.div`
  background: ${BRAND.white};
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);
  position: relative;
  overflow: visible;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: ${BRAND.lime};
    border-radius: 16px 16px 0 0;
  }
`;

// --- Hover Tile Wrapper ---
const splatterAppear = keyframes`
  from { opacity: 0; transform: scale(0); }
  to { opacity: 1; transform: scale(1); }
`;

export const HoverTile = styled.div`
  background: ${BRAND.white};
  border: 2px solid ${BRAND.borderLight};
  border-radius: 16px;
  padding: 32px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: visible;

  .tile-icon {
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    color: ${BRAND.black};
  }

  .hover-splatter {
    opacity: 0;
    transform: scale(0);
    transition: all 0.3s ease;
  }

  &:hover {
    border-color: ${BRAND.lime};
    border-width: 3px;
    box-shadow: 0 8px 32px rgba(76, 175, 39, 0.15), 0 2px 8px rgba(0, 0, 0, 0.05);
    transform: translateY(-2px);

    .tile-icon {
      color: ${BRAND.lime};
    }

    .hover-splatter {
      opacity: 1;
      transform: scale(1);
      animation: ${splatterAppear} 0.4s ease-out both;
    }
  }

  &:active {
    transform: translateY(0);
  }
`;
