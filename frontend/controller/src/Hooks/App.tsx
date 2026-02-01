import { useEffect, useState, useRef } from "react";
import { type WaitingRoomMessage, type BackendWaitingMessage } from "./types";
import { useRemote } from "./useRemote";
import { ControlInterface } from "./ControlInterfac";
import LandingPage from "../Components/Interface";
import AuthModal from "../Components/CodePopUp";
import WelcomeScreen from "../Components/WelcomeScreen.tsx";
import { fetchBackendIP } from "./getApi.ts";

export default function App() {
  const [data, setData] = useState<WaitingRoomMessage | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [activeModal, setActiveModal] = useState<"qr" | "pin" | null>(null);
  const [host, setHost] = useState<string>("127.0.0.1");
  const [isLoadingHost, setIsLoadingHost] = useState(true);

  // Récupération automatique de l'IP du backend
  useEffect(() => {
    const initializeHost = async () => {
      
      const urlParams = new URLSearchParams(window.location.search);
      const backendUrlParam = urlParams.get('backend_url');

      if (backendUrlParam) {
        // Utiliser le backend_url de l'URL provenant  du QR code
        const hostOnly = backendUrlParam.replace(':8000', '');
        console.log('🔍 Backend URL détecté depuis QR code:', hostOnly);
        setHost(hostOnly);
        setIsLoadingHost(false);
        return;
      }

      //  récupération auto de l'IP
      if (
        window.location.hostname === "localhost" ||
        window.location.hostname === "127.0.0.1"
      ) {
        const ip = await fetchBackendIP();
        setHost(ip);
      } else {
        setHost(window.location.hostname);
      }
      setIsLoadingHost(false);
    };

    initializeHost();
  }, []);

  const WS_WAITING_URL = `ws://${host}:8000/ws/waiting`;

  const { verifyAuth, connectWS, sendCommand, disconnect } = useRemote(
    `${host}:8000`
  );

  const handleVerify = async (id?: string, pinCode?: string) => {
    const res = await verifyAuth({ challenge_id: id, pin: pinCode });
    if (res.ok && res.result) {
      sessionStorage.setItem("device_token", res.result.device_token);
      connectWS(res.result.device_token);
      connectWS(res.result.device_token);
      setIsAuthenticated(true);
      setShowWelcome(true); 
      setActiveModal(null);
    } else {
      alert("Erreur: " + res.error);
    }
  };

  // Auto-login depuis QR code (si URL contient backend_url + challenge_id)
  useEffect(() => {
    const autoLoginFromQRCode = async () => {
    
      const urlParams = new URLSearchParams(window.location.search);
      const backendUrlParam = urlParams.get('backend_url');
      const challengeIdParam = urlParams.get('challenge_id');

      
      if (backendUrlParam && challengeIdParam && !isAuthenticated) {
        console.log(' Auto-login depuis QR code...');
        console.log('   Backend:', backendUrlParam);
        console.log('   Challenge ID:', challengeIdParam);

        try {
          // S'authentifier automatiquement avec le challenge_id
          console.log(' Envoi de la demande d\'authentification auto...');
          await handleVerify(challengeIdParam);

          // Nettoyer l'URL retirer les paramètres sensibles
          window.history.replaceState({}, '', window.location.pathname);
          console.log(' Auto-login terminé, URL nettoyée');
        } catch (error) {
          console.error(' Erreur critique lors de l\'auto-login:', error);
          alert('Erreur d\'authentification automatique. Veuillez réessayer manuellement.');
        }
      } else if (!backendUrlParam || !challengeIdParam) {
        console.log('Pas de paramètres d\'auto-login dans l\'URL.');
      }
    };

    // Attendre que le host soit initialisé avant de tenter l'auto-login
    if (!isLoadingHost) {
      autoLoginFromQRCode();
    }
  }, [isLoadingHost, isAuthenticated]);

  const wsWaiting = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (isAuthenticated) return;

    let isMounted = true;

    const connect = () => {

      if (wsWaiting.current?.readyState === WebSocket.CONNECTING || wsWaiting.current?.readyState === WebSocket.OPEN) {
        return;
      }

      console.log("Connexion au WebSocket de salle d'attente...");
      const socket = new WebSocket(WS_WAITING_URL);
      wsWaiting.current = socket;

      socket.onmessage = (event) => {
        if (!isMounted) return;

        try {
          const msg: BackendWaitingMessage = JSON.parse(event.data);

          //  Réception des codes pin ou qr 
          if (msg.type === "NEW_CHALLENGE") {

            if (msg.data.challenge_id && msg.data.pin) {
              setData({
                challenge_id: msg.data.challenge_id,
                pin: msg.data.pin
              });
            } else {
              console.warn("Message NEW_CHALLENGE reçu avec des données incomplètes", msg.data);
            }
          }

          //  Succès d'authentification
          if (msg.type === "AUTHENTIFICATION_SUCCESS") {
            const authData = msg.data as unknown as { device_token: string };
            if (authData.device_token) {
              sessionStorage.setItem("device_token", authData.device_token);
              connectWS(authData.device_token);
              setIsAuthenticated(true);
              setShowWelcome(true);
              setActiveModal(null);
            }
          }
        } catch (err) {
          console.error("Erreur parsing JSON:", err);
        }
      };

      socket.onerror = (error) => {
        console.error("Erreur WebSocket détectée:", error);
      };

      socket.onclose = () => {
        console.log("WebSocket de salle d'attente fermé.");
      };
    };

    const timer = setTimeout(() => {
      connect();
    }, 500);
    return () => {
      clearTimeout(timer);
      isMounted = false;
      if (wsWaiting.current) {
        wsWaiting.current.close();
        wsWaiting.current = null;
      }
    };

   
    return () => {
      isMounted = false;
      if (wsWaiting.current) {
        wsWaiting.current.close();
        wsWaiting.current = null;
      }
    };
  }, [WS_WAITING_URL, isAuthenticated, connectWS]);

  // VUE CONTRÔLE (TÉLÉCOMMANDE)
  if (isAuthenticated) {
    if (showWelcome) {
      return <WelcomeScreen onStart={() => setShowWelcome(false)} />;
    }

    return (
      <div className="min-h-screen bg-[#050508] text-white flex flex-col items-center justify-center p-6">
        <ControlInterface
          onCommand={sendCommand}
          onDisconnect={() => {
            disconnect();
            setIsAuthenticated(false);
            sessionStorage.removeItem("device_token");
          }}
        />
      </div>
    );
  }


  if (isLoadingHost) {
    return (
      <div className="min-h-screen bg-[#050508] text-white flex flex-col items-center justify-center p-6">
        <div className="text-center">
          <div className="mb-4 text-2xl">🔄</div>
          <p className="text-gray-400">Connexion au backend...</p>
        </div>
      </div>
    );
  }

  
  return (
    <div className="relative min-h-screen bg-[#050508] overflow-hidden">
      <LandingPage
        host={host}
        onOpenQR={() => setActiveModal("qr")}
        onOpenPIN={() => setActiveModal("pin")}
      />

      {activeModal && (
        <AuthModal
          type={activeModal}
          data={data}
          backendUrl={`${host}:8000`}
          onClose={() => setActiveModal(null)}
          onVerify={handleVerify}
        />
      )}
    </div>
  );
}