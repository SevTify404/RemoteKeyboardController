import { X } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';


export default function CodePopUp({ type, data, backendUrl, onClose }: any) {

  // Extraire l'IP du backendUrl sans le port 
  const hostIp = backendUrl.split(':')[0];

  // Construire l'URL du frontend avec l'IP correcte et le port sur lequel  que le pc est 
  const currentPort = window.location.port;
  const frontendUrl = `http://${hostIp}:${currentPort}`;

  const qrCodeUrl = data?.challenge_id
    ? `${frontendUrl}/?backend_url=${encodeURIComponent(backendUrl)}&challenge_id=${data.challenge_id}`
    : '';

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">

      <div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={onClose} />


      <div className="relative bg-[#0f1115] border border-white/10 p-10 rounded-[2.5rem] w-full max-w-md shadow-2xl animate-in fade-in zoom-in duration-300">
        <button onClick={onClose} className="absolute top-6 right-6 text-gray-500 hover:text-white">
          <X size={24} />
        </button>

        {type === 'qr' ? (
          <div className="flex flex-col items-center gap-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2">Scanner le Code</h2>
              <p className="text-sm text-gray-500">Utilisez votre mobile pour l'authentification</p>
            </div>
            <div className="bg-white p-6 rounded-3xl shadow-[0_0_30px_rgba(59,130,246,0.3)]">
              {qrCodeUrl ? (
                <QRCodeSVG value={qrCodeUrl} size={200} fgColor="#000" />
              ) : (
                <div className="w-[200px] h-[200px] flex items-center justify-center text-black">Génération...</div>
              )}
            </div>

          </div>
        ) : (
          <div className="flex flex-col items-center gap-8">
            <div className="text-center">
              <h2 className="text-2xl text-white font-bold mb-2">Code de Sécurité</h2>
              <p className="text-sm text-white">Saisissez le code PIN affiché </p>
            </div>
            <div className="flex gap-3">
              {(data?.pin || "000000").split('').map((digit: string, i: number) => (
                <div key={i} className="w-12 h-16 bg-white border-white/10 rounded-xl flex items-center justify-center text-3xl font-mono font-bold">
                  {digit}
                </div>
              ))}
            </div>

          </div>
        )}
      </div>
    </div>
  );
}