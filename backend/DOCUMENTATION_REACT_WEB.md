# 📱 Guide Complet du Workflow d'Authentification – React Web

## Table des matières
1. [Aperçu du workflow](#aperçu-du-workflow)
2. [Route POST `/auth/verify`](#route-post-authverify)
3. [WebSocket `/ws/control-panel`](#websocket-wscontrol-panel)
4. [Structure complète des données](#structure-complète-des-données)
5. [Gestion des erreurs](#gestion-des-erreurs)
6. [Points clés d'implémentation](#points-clés-dimplémentation)

---

## Aperçu du workflow

### Étapes principales

```
1. POST /auth/verify
   ├─ Envoyer: { challenge_id: "UUID" } OU { pin: "123456" }
   └─ Recevoir: { ok: true, result: { device_token, session_token, ... } }

2. Connexion WebSocket control-panel
   ├─ URL: ws://[SERVER]/ws/control-panel?device_token=[TOKEN]
   └─ État: Connecté et prêt à envoyer des commandes

3. Envoi de commandes
   ├─ Message: { message_type: "command", payload: { command: "UP" } }
   └─ Réception: { type: "COMMAND", data: { succes: true/false, error?: "..." } }

4. Déconnexion
   └─ Message: { message_type: "disconnect", payload: null }
```

---

## Route POST `/auth/verify`

### 📍 Endpoint

```
POST http://[SERVER_HOST]/auth/verify
Content-Type: application/json
```

### 📤 Structure de la requête

**Schéma Pydantic (backend) :**
```python
class VerifyAuthRequest(BaseModel):
    challenge_id: Optional[UUID] = None      # UUID du QR code (scanné)
    pin: Optional[str] = None                # PIN à 6 chiffres (saisi manuellement)
    # ⚠️ Au moins UN des deux doit être fourni (non-null)
```

**JSON à envoyer :**

**Cas 1 : Authentification par Challenge ID (QR Code)**
```json
{
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "pin": null
}
```

**Cas 2 : Authentification par PIN (saisie manuelle)**
```json
{
  "challenge_id": null,
  "pin": "847392"
}
```

### 📥 Structure de la réponse

**Réponse réussie (`ok: true`)**

```python
class VerifyAuthResponse(BaseModel):
    device_id: UUID                    # Identifie votre appareil
    device_token: str                  # Token pour WebSocket control-panel
    session_token: str                 # Token de session actuelle
    session_expires_at: Optional[datetime]  # Expiration (ISO 8601)
```

**JSON reçu (succès):**
```json
{
  "ok": true,
  "result": {
    "device_id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "device_token": "DjHvR4_bZ8kP2wX9nQ5lM7vJ3sA6tY1uW0",
    "session_token": "aBcDeF1gHiJkLmNoPqRsT2uVwXyZ3aB4cD",
    "session_expires_at": "2024-12-21T15:35:00"
  },
  "error": null
}
```

### ❌ Réponse d'erreur (`ok: false`)

**Erreurs possibles:**
```python
# Enum ErrorMessages du backend
CHALLENGE_USED = "CHALLENGE IS USED"                    # Challenge déjà utilisé
UNEXIST_CHALLENGE = "CHALLENGE NOT FOUND"               # Challenge n'existe pas
INVALID_PIN = "INVALID PIN"                             # PIN incorrect
UNFOUND_PIN = "PIN NOT FOUND"                           # PIN inexistant
BLOCKED_PIN = "PIN BLOCKED DUE TO MAX ATTEMPTS"         # > 3 tentatives
CHALLENGE_TIME_OUT = "CHALLENGE HAS EXPIRED"            # > 5 minutes
```

**JSON reçu (erreur):**
```json
{
  "ok": false,
  "result": null,
  "error": "INVALID_PIN or BLOCKED_PIN or UNFOUND_PIN"
}
```

### ⏱️ Logique serveur (ce qui se passe)

**Si `challenge_id` fourni:**
1. ✅ Vérifier que le challenge existe
2. ✅ Vérifier qu'il n'a pas expiré (> 5 min)
3. ✅ Vérifier qu'il n'a pas déjà été utilisé
4. ✅ Marquer le challenge comme utilisé

**Si `pin` fourni:**
1. ✅ Vérifier que le PIN existe
2. ✅ Vérifier qu'il n'a pas expiré (> 5 min)
3. ✅ Vérifier qu'il n'a pas été bloqué (> 3 tentatives)
4. ✅ Vérifier le challenge associé au PIN
5. ✅ Marquer le PIN comme utilisé
6. ✅ Incrémenter les tentatives si erreur

**Succès:**
1. ✅ Générer un `device_token` (valable 1 heure)
2. ✅ Générer un `session_token` (valable 1 heure)
3. ✅ Envoyer une notification WebSocket à l'écran d'attente
4. ✅ Déconnecter le WebSocket d'attente
5. ✅ Retourner les tokens

---

## WebSocket `/ws/control-panel`

### 📍 URL de connexion

```
ws://[SERVER_HOST]/ws/control-panel?device_token=[YOUR_DEVICE_TOKEN]
```

**Point crucial:** Le `device_token` reçu lors du POST `/auth/verify` **DOIT** être passé en paramètre de requête.

**Exemple:**
```
ws://192.168.1.100:8000/ws/control-panel?device_token=DjHvR4_bZ8kP2wX9nQ5lM7vJ3sA6tY1uW0
```

### 📤 Messages à envoyer (Client → Serveur)

**Schéma Pydantic:**
```python
class AvailableMessageTypes(str, Enum):
    COMMAND = "command"              # Envoyer une commande clavier
    DISCONNECT = "disconnect"        # Demander la déconnexion
    STATUS_UPDATE = "status_update"  # Mise à jour de statut (non implémenté)
    TYPING = "typing"                # Taper du texte

class PayloadFormat(BaseModel):
    command: Optional[AvailableKeys] = None       # La commande à exécuter
    message: Optional[str] = None                 # Message de statut
    text_to_type: Optional[str] = None            # Texte à taper

class ControlPanelWSMessage(BaseModel):
    message_type: AvailableMessageTypes
    payload: Optional[PayloadFormat] = None
```

**Commandes disponibles (`AvailableKeys`):**
```python
# Navigation
"UP"        # Flèche haut
"DOWN"      # Flèche bas
"LEFT"      # Flèche gauche
"RIGHT"     # Flèche droite
"ENTER"     # Entrée

# Média
"MUTE"              # Muet
"VOLUME_UP"         # Volume +
"VOLUME_DOWN"       # Volume -

# Clavier
"COPY"              # Ctrl+C
"PASTE"             # Ctrl+V
"SELECT_ALL"        # Ctrl+A
"ALT_TAB"           # Alt+Tab

# Présentation
"START_PRESENTATION"  # F5
"END_PRESENTATION"    # Esc
```

**Exemples de messages JSON:**

**1. Appuyer sur une touche (UP)**
```json
{
  "message_type": "command",
  "payload": {
    "command": "UP",
    "text_to_type": null,
    "message": null
  }
}
```

**2. Copier (Ctrl+C)**
```json
{
  "message_type": "command",
  "payload": {
    "command": "COPY",
    "text_to_type": null,
    "message": null
  }
}
```

**3. Taper du texte**
```json
{
  "message_type": "typing",
  "payload": {
    "command": null,
    "text_to_type": "Bonjour le monde!",
    "message": null
  }
}
```

**4. Démarrer une présentation (F5)**
```json
{
  "message_type": "command",
  "payload": {
    "command": "START_PRESENTATION",
    "text_to_type": null,
    "message": null
  }
}
```

**5. Demander la déconnexion**
```json
{
  "message_type": "disconnect",
  "payload": null
}
```

### 📥 Messages reçus (Serveur → Client)

**Schéma Pydantic:**
```python
class OutControlPanelWSMessage(BaseModel):
    succes: bool                              # ⚠️ Attention: "succes" pas "success"
    data: Optional[ControlPanelWSMessage]     # Écho du message envoyé
    error: Optional[str]                      # Message d'erreur si succes=false

class WsPayloadMessage(BaseModel):
    type: WssTypeMessage                      # "COMMAND" ou "NOTIFY"
    data: Union[OutControlPanelWSMessage, Notification]
```

**Exemples de messages reçus:**

**1. Succès d'une commande**
```json
{
  "type": "COMMAND",
  "data": {
    "succes": true,
    "data": {
      "message_type": "command",
      "payload": {
        "command": "UP",
        "text_to_type": null,
        "message": null
      }
    },
    "error": null
  }
}
```

**2. Erreur de commande**
```json
{
  "type": "COMMAND",
  "data": {
    "succes": false,
    "data": null,
    "error": "Données de commandes reçu mais mal formatés, Impossible de traiter"
  }
}
```

**3. Notification du serveur**
```json
{
  "type": "NOTIFY",
  "data": {
    "message": "Le client s'est déconnecté"
  }
}
```

---

## Structure complète des données

### Flux d'authentification complet

```
CLIENT (React)                    SERVEUR (FastAPI)

1. POST /auth/verify
   ├─ Body: {
   │   challenge_id: UUID ou null
   │   pin: string ou null
   │ }
   └─────────────────────────────>
                                  ✓ Valide challenge/PIN
                                  ✓ Génère tokens
                                  ✓ Notifie WebSocket waiting
                                  ✓ Déconnecte WebSocket waiting
                    <─────────────
   ← Reçoit: {
   │   ok: true,
   │   result: {
   │     device_id: UUID,
   │     device_token: string,
   │     session_token: string,
   │     session_expires_at: ISO8601
   │   }
   │ }

2. Ouvre WebSocket control-panel
   avec device_token en paramètre
   ├─ URL: ws://[SERVER]/ws/control-panel?device_token=[TOKEN]
   └─────────────────────────────>
                                  ✓ Vérifie device_token
                                  ✓ Accepte la connexion
                                  ✓ Démarre le contrôleur clavier
                    <─────────────
   ← Connexion établie

3. Envoie commandes
   ├─ {
   │   message_type: "command",
   │   payload: { command: "UP" }
   │ }
   └─────────────────────────────>
                                  ✓ Exécute la commande
                                  ✓ Envoie confirmation
                    <─────────────
   ← Reçoit: {
   │   type: "COMMAND",
   │   data: { succes: true, ... }
   │ }

4. Déconnexion
   ├─ { message_type: "disconnect", payload: null }
   └─────────────────────────────>
                                  ✓ Ferme la connexion
                                  ✓ Arrête le contrôleur
                                  ✓ Notifie admin panel
```

---

## Gestion des erreurs

### Codes d'erreur `/auth/verify`

| Erreur | Cause | Action utilisateur |
|--------|-------|-------------------|
| `UNEXIST_CHALLENGE` | Le QR code n'existe pas | Rafraîchir la page, scanner un nouveau QR |
| `CHALLENGE_USED` | Le QR code a déjà été utilisé | Rafraîchir la page, scanner un nouveau QR |
| `CHALLENGE_TIME_OUT` | Le QR code a expiré (> 5 min) | Rafraîchir la page, scanner un nouveau QR |
| `INVALID_PIN` | Le PIN saisi ne correspond pas | Vérifier et resaisir |
| `UNFOUND_PIN` | Le PIN n'existe pas | Vérifier et resaisir |
| `BLOCKED_PIN` | Trop de tentatives (> 3) | Attendre 5 minutes avant de réessayer |

### Gestion côté React

```javascript
// Exemple de mappage d'erreur
const errorMessages = {
  'CHALLENGE_USED': 'Ce QR code a déjà été utilisé. Veuillez rafraîchir.',
  'UNEXIST_CHALLENGE': 'Le QR code n\'est pas valide.',
  'CHALLENGE_TIME_OUT': 'Le QR code a expiré. Veuillez rafraîchir.',
  'INVALID_PIN': 'Le PIN saisi est incorrect.',
  'UNFOUND_PIN': 'Le PIN n\'existe pas.',
  'BLOCKED_PIN': 'Trop de tentatives. Attendez 5 minutes.',
};

const handleError = (error) => {
  const message = errorMessages[error] || 'Erreur d\'authentification';
  showUserAlert(message);
};
```

---

## Points clés d'implémentation

### ✅ À FAIRE

1. **Validation stricte du PIN**
   - Vérifier que le PIN fait exactement 6 chiffres
   - Accepter uniquement des caractères numériques

2. **Gestion du device_token**
   - Toujours le passer en paramètre d'URL pour le WebSocket
   - Ne jamais l'inclure dans le body de la requête
   - Le stocker de manière sécurisée (sessionStorage, pas localStorage)

3. **État de connexion**
   - Afficher un indicateur visuel de connexion WebSocket
   - Gérer les déconnexions inattendues
   - Implémenter un système de reconnexion automatique

4. **Timeout et limites**
   - PIN valable 5 minutes (afficher le timer)
   - Challenge valable 5 minutes
   - Retry avec backoff exponentiel en cas d'erreur réseau

### ❌ À ÉVITER

1. Ne pas réutiliser un token expiré
2. Ne pas envoyer de PIN après 3 tentatives échouées
3. Ne pas oublier le device_token en paramètre WebSocket
4. Ne pas stocker les tokens en localStorage sans chiffrement
5. Ne pas afficher les UUIDs bruts à l'utilisateur
6. Ne pas laisser la connexion WebSocket ouverte sans heartbeat

### 🔐 Sécurité

```javascript
// Stockage sécurisé des tokens
// ✅ BON
sessionStorage.setItem('device_token', token);  // Tokens de session
sessionStorage.setItem('session_token', token);

// ❌ MAUVAIS
localStorage.setItem('device_token', token);  // Persistant, visible en clair
```

### 📊 Exemple de flux complet en React

```javascript
// 1. Appeler /auth/verify
const response = await fetch('http://[SERVER]/auth/verify', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    challenge_id: scannedQRCode || null,
    pin: userPinInput || null
  })
});

const data = await response.json();

if (data.ok) {
  // 2. Stocker les tokens
  const { device_token, session_token } = data.result;
  sessionStorage.setItem('device_token', device_token);
  
  // 3. Connecter au WebSocket
  const ws = new WebSocket(
    `ws://[SERVER]/ws/control-panel?device_token=${device_token}`
  );
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.data.succes) {
      // Commande exécutée ✅
    } else {
      // Erreur: message.data.error
    }
  };
  
  // 4. Envoyer une commande
  ws.send(JSON.stringify({
    message_type: 'command',
    payload: { command: 'UP' }
  }));
  
  // 5. Déconnecter proprement
  ws.send(JSON.stringify({
    message_type: 'disconnect',
    payload: null
  }));
  ws.close();
} else {
  // Afficher l'erreur: data.error
  showError(data.error);
}
```

---

## Résumé des étapes critiques

| Étape | Action | Validation |
|-------|--------|-----------|
| 1 | POST `/auth/verify` | `ok: true` et `device_token` présent |
| 2 | Récupérer `device_token` | Non-null et non-vide |
| 3 | Ouvrir WebSocket avec token | Connexion établie (`readyState === 1`) |
| 4 | Envoyer commandes | Format JSON strict respecté |
| 5 | Traiter réponses | Vérifier `data.succes` et `data.error` |
| 6 | Déconnecter proprement | Message `disconnect` puis `close()` |

