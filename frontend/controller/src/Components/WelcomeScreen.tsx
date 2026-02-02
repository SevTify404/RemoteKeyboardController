import { Play, Keyboard } from 'lucide-react';

export default function WelcomeScreen({ onStart }: { onStart: () => void }) {
    return (
        <div className="min-h-screen bg-[#050508] text-white flex flex-col items-center justify-center p-8 text-center animate-in fade-in duration-700">

            {/* Icone */}
            <div className="relative mb-8">
                <div className="absolute inset-0 bg-blue-500/20 blur-[40px] rounded-full animate-pulse" />
                <div className="relative bg-white/5 border border-white/10 p-8 rounded-full shadow-2xl animate-in zoom-in duration-500 delay-100">
                    <Keyboard  size={64} className="text-green-500 drop-shadow-[0_0_15px_rgba(34,197,94,0.5)]" />
                </div>
            </div>

   
            <div className="space-y-4 mb-12 max-w-xs mx-auto animate-in slide-in-from-bottom-4 duration-700 delay-200">
                <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-br from-white to-gray-500 bg-clip-text text-transparent">
                    Connecté !
                </h1>
                <p className="text-gray-400 text-lg leading-relaxed">
                    Votre téléphone est maintenant connecté a votre ordinateur.
                </p>
            </div>

            {/* Bouton Commencer */}
            <button
                onClick={onStart}
                className="group relative w-full max-w-xs animate-in slide-in-from-bottom-8 duration-700 delay-300"
            >
                <div className="absolute inset-0 bg-gradient-to-r from-black to-gray-600 rounded-2xl blur-lg opacity-50 group-hover:opacity-75 transition-opacity duration-500" />
                <div className="relative bg-white text-black py-4 rounded-2xl font-bold text-lg tracking-wide uppercase flex items-center justify-center gap-3 hover:scale-[1.02] active:scale-[0.98] transition-all duration-200">
                    <span>Commencer</span>
                    <Play size={20} fill="black" className="group-hover:translate-x-1 transition-transform" />
                </div>
            </button>

            {/* Footer */}
            <p className="fixed bottom-8 text-xs text-gray-600 font-mono tracking-widest uppercase opacity-50 animate-in fade-in duration-1000 delay-500">
               Equipe de IAI-OPENSCOURCE
            </p>
        </div>
    );
}
