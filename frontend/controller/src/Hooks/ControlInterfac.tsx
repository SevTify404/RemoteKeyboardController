import { 
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, CornerDownLeft, 
  Volume2, Volume1, VolumeX, Play, Square, LogOut, 
  Copy, Clipboard, MousePointer, AppWindow 
} from 'lucide-react';
import { type CommandKey } from './types';

interface Props {
  onCommand: (cmd: CommandKey) => void;
  onDisconnect: () => void;
}

const ControlBtn = ({ 
  cmd, 
  icon: Icon, 
  color = "bg-white/[0.03]", 
  label,
  onCommand 
}: { 
  cmd: CommandKey; 
  icon: any; 
  color?: string;
  label?: string;
  onCommand: (cmd: CommandKey) => void; 
}) => (
  <button 
    onClick={() => onCommand(cmd)}
    className={`${color} border border-white/10 hover:bg-white/10 p-5 rounded-[1.5rem] active:scale-90 transition-all flex flex-col items-center justify-center gap-2 group`}
  >
    <Icon size={24} className="text-gray-400 group-hover:text-white transition-colors" />
    {label && <span className="text-[9px] font-black uppercase tracking-widest text-gray-500 group-hover:text-gray-300">{label}</span>}
  </button>
);

export const ControlInterface = ({ onCommand, onDisconnect }: Props) => {
  return (
    <div className="flex flex-col gap-6 w-full max-w-sm animate-in fade-in zoom-in duration-500">
      
   
      <div className="bg-white/[0.02] border border-white/5 p-6 rounded-[2.5rem] backdrop-blur-xl">
        <div className="grid grid-cols-3 gap-3">
          <div /> 
          <ControlBtn cmd="UP" icon={ChevronUp} onCommand={onCommand} /> 
          <div />
          
          <ControlBtn cmd="LEFT" icon={ChevronLeft} onCommand={onCommand} />
          <ControlBtn cmd="ENTER" icon={CornerDownLeft} color="bg-white text-black" onCommand={onCommand} />
          <ControlBtn cmd="RIGHT" icon={ChevronRight} onCommand={onCommand} />
          
          <div /> 
          <ControlBtn cmd="DOWN" icon={ChevronDown} onCommand={onCommand} /> 
          <div />
        </div>
      </div>

      
      <div className="grid grid-cols-4 gap-3">
        <ControlBtn cmd="COPY" icon={Copy} label="Copy" onCommand={onCommand} />
        <ControlBtn cmd="PASTE" icon={Clipboard} label="Paste" onCommand={onCommand} />
        <ControlBtn cmd="SELECT_ALL" icon={MousePointer} label="All" onCommand={onCommand} />
        <ControlBtn cmd="ALT_TAB" icon={AppWindow} label="Tab" onCommand={onCommand} />
      </div>

    
      <div className="bg-white/[0.02] border border-white/5 p-4 rounded-3xl flex items-center gap-3">
        <div className="flex-1 grid grid-cols-3 gap-2">
            <button onClick={() => onCommand("VOLUME_DOWN")} className="p-4 bg-white/5 rounded-2xl hover:bg-white/10 text-gray-400 flex justify-center"><Volume1 size={20}/></button>
            <button onClick={() => onCommand("MUTE")} className="p-4 bg-white/5 rounded-2xl hover:bg-white/10 text-rose-500 flex justify-center"><VolumeX size={20}/></button>
            <button onClick={() => onCommand("VOLUME_UP")} className="p-4 bg-white/5 rounded-2xl hover:bg-white/10 text-gray-400 flex justify-center"><Volume2 size={20}/></button>
        </div>
      </div>

     
      <div className="grid grid-cols-2 gap-4">
        <button 
          onClick={() => onCommand("START_PRESENTATION")} 
          className="bg-white text-black py-4 rounded-2xl flex items-center justify-center gap-3 font-black text-[10px] tracking-[0.2em] hover:bg-gray-200 transition-all uppercase"
        >
          <Play size={16} fill="black"/> Start F5
        </button>
        <button 
          onClick={() => onCommand("END_PRESENTATION")} 
          className="bg-white/5 border border-white/10 text-white py-4 rounded-2xl flex items-center justify-center gap-3 font-black text-[10px] tracking-[0.2em] hover:bg-white/10 transition-all uppercase"
        >
          <Square size={16} fill="white"/> Esc
        </button>
      </div>

    
      <button 
        onClick={onDisconnect} 
        className="mt-4 group flex items-center justify-center gap-2 text-gray-600 hover:text-rose-500 transition-all py-2 text-[10px] font-black uppercase tracking-[0.3em]"
      >
        <LogOut size={14} className="group-hover:-translate-x-1 transition-transform" /> 
        Terminer la session
      </button>

    </div>
  );
};