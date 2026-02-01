import { Github, Users, ChevronRight } from 'lucide-react';
import { motion } from "framer-motion";

const membres = [
  { name: "freeze667", contributions: "Frontend", url: "https://github.com/sabour-agoro" },
  { name: "nemesis228ux", contributions: "Backend", url: "https://github.com/nemesis228ux" },
  { name: "SevTify404", contributions: "Backend", url: "https://github.com/SevTify404" },
  { name: "Paulin ", contributions: "Mobile", url: "https://github.com/KOUTOATI" },
  { name: "fwmad", contributions: "Frontend", url: "https://github.com/fwmad" },
];

export default function LandingPage({ host, onOpenQR, onOpenPIN }: any) {
  return (
    <div className="bg-black text-white font-sans scroll-smooth">
      
      
      <nav className="fixed top-0 w-full flex flex-col md:flex-row justify-between items-center px-6 md:px-12 py-8 z-50 gap-4">
        <div className="flex items-center gap-2 font-bold text-xl uppercase tracking-tighter">
         
        </div>
        
        <div className="bg-white/5 backdrop-blur-md px-6 py-2 rounded-full border border-white/10 flex gap-8 text-sm font-medium text-gray-400">
          <a href="#" className="hover:text-white transition-colors text-white">Home</a>
          <a href="#equipe" className="hover:text-white transition-colors flex items-center gap-1">
            <Users size={14}/> Voir l'équipe
          </a>
          <a href="https://github.com/SevTify404/RemoteKeyboardController.git" target="_blank" className="hover:text-white transition-colors flex items-center gap-1">
            <Github size={14}/> GitHub
          </a>
        </div>

        <div className="text-xs font-mono text-white bg-white/5 px-4 py-2 rounded-full border border-blue-500/20 uppercase tracking-widest backdrop-blur-md">
          Addresse IP: {host}
        </div>
      </nav>

     
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 text-center overflow-hidden">
        
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[20%] right-[-5%] w-[600px] h-[600px] bg-gray-600/20 blur-[150px] rounded-full" />
          <div className="absolute bottom-[-10%] left-[-5%] w-[500px] h-[500px] bg-gray-600/15 blur-[130px] rounded-full" />
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10"
        >
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter mb-6 leading-[0.9]">
            Prenez le contrôle <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-100 to-gray-500">
              de votre ordinateur 
            </span>
          </h1>

          <p className="max-w-xl mx-auto text-gray-400 text-lg mb-12 leading-relaxed">
            Contrôlez votre ordinateur à distance avec votre téléphone 
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={onOpenQR}
              className="px-8 py-4 bg-white text-black font-bold rounded-full hover:bg-gray-200 transition-all flex items-center justify-center gap-2"
            >
              Scanner QR <ChevronRight size={18}/>
            </button>
            <button 
              onClick={onOpenPIN}
              className="px-8 py-4 bg-white/5 border border-white/10 backdrop-blur-md text-white font-bold rounded-full hover:bg-white/10 transition-all"
            >
              Voir le PIN
            </button>
          </div>
        </motion.div>
      </section>
      {/*Partie Equiepe */}
 <section id="equipe" className="min-h-screen w-full bg-black text-white flex items-center justify-center py-24 px-4">
      <div className="w-full max-w-7xl">
        
        <motion.div 
          initial={{ opacity: 0, y: -30 }} 
          animate={{ opacity: 1, y: 0 }} 
          transition={{ duration: .8 }} 
          className="text-center mb-16"
        >
          <h2 className="text-5xl md:text-6xl font-black tracking-tight">
            Les contributeurs au projet <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-neutral-400">REMOTEKEYBOARDCONTROLLER</span>
          </h2>
        </motion.div>
       
        <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-12 place-items-center">
          {membres.map((m, index) => (
            <motion.div
              key={m.name}
              className="group relative p-[2px] rounded-3xl w-64 
                         bg-gradient-to-br from-neutral-900 to-black overflow-hidden
                         transition-all duration-700 hover:scale-110 hover:rotate-[1deg]
                         hover:from-neutral-700 hover:to-neutral-900 cursor-pointer"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * .2, duration: .7 }}
              whileHover={{ y: -10 }}
            >
             
              <a href={m.url} target="_blank" rel="noopener noreferrer" className="block relative h-full">
                
                <div className="absolute inset-0 bg-gradient-to-r from-white/10 via-white/40 to-transparent
                                opacity-0 group-hover:opacity-100 blur-2xl transition-all duration-700"></div>

                <div className="relative rounded-3xl h-full p-8 backdrop-blur-xl bg-white/5 border border-white/10
                                group-hover:border-white/30 transition-all duration-500 text-center">

                  <motion.h3 
                    className="text-xl font-semibold tracking-wide"
                    whileHover={{ letterSpacing: "1.5px" }}
                    transition={{ duration: .4 }}
                  >
                    {m.name}
                  </motion.h3>

                  <motion.p 
                    className="mt-2 text-neutral-300 text-sm"
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: .4, duration: .6 }}
                  >
                    {m.contributions}
                  </motion.p>

                 
                  {/* <span className="block w-0 bg-white h-[2px] mx-auto mt-3 transition-all duration-500 group-hover:w-24"></span> */}
                </div>
              </a>
            </motion.div>
          ))}
        </div>
      </div>
    </section>

    </div>
  );
}