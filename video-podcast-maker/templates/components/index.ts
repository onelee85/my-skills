// Layouts
export { Scale4K, FullBleedLayout, PaddedLayout } from "./layouts";

// Animations
export {
  useEntrance, useExit, useCounter, useBarFill, getPresentation,
  useFloat, usePulse, useGradientShift, useOpacityWave,
  useTextReveal, useCharReveal, staggerDelay,
  useDrawOn, useStaggeredDrawOn,
} from "./animations";

// Animated backgrounds
export {
  MovingGradient, FloatingShapes, GridPattern, GlowOrb, AccentLine,
} from "./AnimatedBackground";

// Section layout presets
export {
  SplitLayout, StatHighlight, ZigzagCards,
  CenteredShowcase, MetricsRow, StepProgress,
} from "./SectionLayouts";

// Content components
export { ComparisonCard } from "./ComparisonCard";
export { Timeline } from "./Timeline";
export { CodeBlock } from "./CodeBlock";
export { QuoteBlock } from "./QuoteBlock";
export { FeatureGrid } from "./FeatureGrid";
export { DataBar } from "./DataBar";
export { StatCounter } from "./StatCounter";
export { FlowChart } from "./FlowChart";
export { IconCard } from "./IconCard";
export { ChapterProgressBar } from "./ChapterProgressBar";
export { MediaSection, MediaGrid } from "./MediaSection";
export { DiagramReveal } from "./DiagramReveal";
export type { DiagramNode, DiagramEdge } from "./DiagramReveal";
export { AudioWaveform } from "./AudioWaveform";
export { LottieAnimation } from "./LottieAnimation";
export { Icon } from "./Icon";
export { ICON_MAP, isEmoji } from "./iconMap";
export { ShortIntroCard } from "./ShortIntroCard";
export { ShortCTACard } from "./ShortCTACard";
