import {
  Rocket, Check, X, Plus, Minus, Play, Pause, ChevronRight,
  Lightbulb, Target, Star, Heart, Flag, Trophy, Zap, Sparkles,
  Code, Terminal, Database, Server, Cloud, Cpu, Globe, Wifi,
  Video, Music, Image, Mic, Camera, Headphones, Volume2,
  DollarSign, TrendingUp, TrendingDown, BarChart3, PieChart, Wallet,
  MessageCircle, Mail, Bell, Share2, Send, Users, User,
  FileText, Folder, Download, Upload, Search, Settings, Lock,
  Calendar, Clock, Timer, AlertCircle, Info, HelpCircle,
  ThumbsUp, ThumbsDown, Bookmark, Eye, EyeOff,
  ArrowRight, ArrowLeft, ArrowUp, ArrowDown, RefreshCw,
  CheckCircle, XCircle, AlertTriangle, Shield, Award,
  Layers, Layout, Grid, List, Package, Box, Puzzle,
  Brain, Wand2, Palette, Brush, Pen, Edit3,
  type LucideIcon,
} from "lucide-react";

export const ICON_MAP: Record<string, LucideIcon> = {
  // Actions
  rocket: Rocket,
  check: Check,
  x: X,
  plus: Plus,
  minus: Minus,
  play: Play,
  pause: Pause,
  "chevron-right": ChevronRight,
  refresh: RefreshCw,

  // Objects
  lightbulb: Lightbulb,
  target: Target,
  star: Star,
  heart: Heart,
  flag: Flag,
  trophy: Trophy,
  zap: Zap,
  sparkles: Sparkles,

  // Tech
  code: Code,
  terminal: Terminal,
  database: Database,
  server: Server,
  cloud: Cloud,
  cpu: Cpu,
  globe: Globe,
  wifi: Wifi,

  // Media
  video: Video,
  music: Music,
  image: Image,
  mic: Mic,
  camera: Camera,
  headphones: Headphones,
  volume: Volume2,

  // Finance
  dollar: DollarSign,
  "trending-up": TrendingUp,
  "trending-down": TrendingDown,
  chart: BarChart3,
  pie: PieChart,
  wallet: Wallet,

  // Communication
  message: MessageCircle,
  mail: Mail,
  bell: Bell,
  share: Share2,
  send: Send,
  users: Users,
  user: User,

  // Files
  file: FileText,
  folder: Folder,
  download: Download,
  upload: Upload,
  search: Search,
  settings: Settings,
  lock: Lock,

  // Time
  calendar: Calendar,
  clock: Clock,
  timer: Timer,

  // Status
  alert: AlertCircle,
  info: Info,
  help: HelpCircle,
  "check-circle": CheckCircle,
  "x-circle": XCircle,
  warning: AlertTriangle,
  shield: Shield,
  award: Award,

  // Interaction
  "thumbs-up": ThumbsUp,
  "thumbs-down": ThumbsDown,
  bookmark: Bookmark,
  eye: Eye,
  "eye-off": EyeOff,

  // Arrows
  "arrow-right": ArrowRight,
  "arrow-left": ArrowLeft,
  "arrow-up": ArrowUp,
  "arrow-down": ArrowDown,

  // Layout
  layers: Layers,
  layout: Layout,
  grid: Grid,
  list: List,
  package: Package,
  box: Box,
  puzzle: Puzzle,

  // Creative
  brain: Brain,
  wand: Wand2,
  palette: Palette,
  brush: Brush,
  pen: Pen,
  edit: Edit3,
};

export const isEmoji = (s: string): boolean => {
  if (s.length > 4) return false;
  return /\p{Emoji}/u.test(s);
};
