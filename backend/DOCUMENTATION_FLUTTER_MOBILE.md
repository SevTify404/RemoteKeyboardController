# 📱 Guide Complet du Workflow d'Authentification – Flutter Mobile

## Table des matières
1. [Aperçu du workflow](#aperçu-du-workflow)
2. [Route POST `/auth/verify`](#route-post-authverify)
3. [WebSocket `/ws/control-panel`](#websocket-wscontrol-panel)
4. [Modèles Dart complets](#modèles-dart-complets)
5. [Gestion des erreurs](#gestion-des-erreurs)
6. [Points clés d'implémentation](#points-clés-dimplémentation)

---

## Aperçu du workflow

### Étapes principales

```
1. Vous recevez challenge_id (du QR scanné) OU pin (saisi manuellement)
   
2. POST /auth/verify
   ├─ Envoyer: { challenge_id: "UUID" } OU { pin: "123456" }
   └─ Recevoir: { ok: true, result: { device_token, session_token, ... } }

3. Connexion WebSocket control-panel
   ├─ URL: ws://[SERVER]/ws/control-panel?device_token=[TOKEN]
   └─ État: Connecté et prêt à envoyer des commandes

4. Envoi de commandes
   ├─ Message: { message_type: "command", payload: { command: "UP" } }
   └─ Réception: { type: "COMMAND", data: { succes: true/false, error?: "..." } }

5. Déconnexion
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

**Modèle Dart à créer:**
```dart
class VerifyAuthRequest {
  final String? challengeId;  // UUID optionnel (du QR Code)
  final String? pin;          // String optionnel (PIN saisi manuellement)

  VerifyAuthRequest({
    this.challengeId,
    this.pin,
  });

  // Validation: au moins un champ doit être non-null
  bool isValid() {
    return (challengeId != null && challengeId!.isNotEmpty) ||
           (pin != null && pin!.isNotEmpty);
  }

  // Convertir en JSON pour envoyer au serveur
  Map<String, dynamic> toJson() {
    return {
      'challenge_id': challengeId,
      'pin': pin,
    };
  }
}
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

```dart
class VerifyAuthResponse {
  final String deviceId;         // UUID - Identifie votre téléphone
  final String deviceToken;      // Token d'authentification principal
  final String sessionToken;     // Token pour cette session
  final DateTime sessionExpiresAt; // Quand la session expire

  VerifyAuthResponse({
    required this.deviceId,
    required this.deviceToken,
    required this.sessionToken,
    required this.sessionExpiresAt,
  });

  // Parser la réponse JSON
  factory VerifyAuthResponse.fromJson(Map<String, dynamic> json) {
    return VerifyAuthResponse(
      deviceId: json['device_id'] as String,
      deviceToken: json['device_token'] as String,
      sessionToken: json['session_token'] as String,
      sessionExpiresAt: DateTime.parse(json['session_expires_at'] as String),
    );
  }

  // Vérifier si le token a expiré
  bool isExpired() => DateTime.now().isAfter(sessionExpiresAt);
}

// Modèle wrapper pour la réponse API
class ApiBaseResponse<T> {
  final bool ok;
  final T? result;    // Présent si ok === true
  final String? error; // Présent si ok === false

  ApiBaseResponse({
    required this.ok,
    this.result,
    this.error,
  });

  factory ApiBaseResponse.fromJson(
    Map<String, dynamic> json,
    T Function(dynamic) fromJsonT,
  ) {
    return ApiBaseResponse(
      ok: json['ok'] as bool? ?? false,
      result: json['ok'] == true && json['result'] != null
          ? fromJsonT(json['result'])
          : null,
      error: json['error'] as String?,
    );
  }
}
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
```dart
enum AuthError {
  challengeUsed,           // Le challenge a déjà été utilisé
  unexistChallenge,        // Le challenge n'existe pas
  invalidPin,              // Le PIN saisi ne correspond pas
  unfoundPin,              // Le PIN n'existe pas
  blockedPin,              // Trop d'essais (max 3)
  challengeTimeOut,        // Le challenge a expiré (> 5 min)
  unknownError,            // Erreur inconnue
}

// Parser les erreurs du serveur
AuthError parseAuthError(String errorMessage) {
  if (errorMessage.contains('CHALLENGE_USED')) return AuthError.challengeUsed;
  if (errorMessage.contains('UNEXIST_CHALLENGE')) return AuthError.unexistChallenge;
  if (errorMessage.contains('INVALID_PIN')) return AuthError.invalidPin;
  if (errorMessage.contains('UNFOUND_PIN')) return AuthError.unfoundPin;
  if (errorMessage.contains('BLOCKED_PIN')) return AuthError.blockedPin;
  if (errorMessage.contains('CHALLENGE_TIME_OUT')) return AuthError.challengeTimeOut;
  return AuthError.unknownError;
}
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

**Exemple Dart:**
```dart
// ❌ MAUVAIS - Sans token
final ws = await WebSocket.connect('ws://localhost:8000/ws/control-panel');

// ✅ BON - Avec token en paramètre
final deviceToken = verifyResponse.deviceToken;
final ws = await WebSocket.connect(
  'ws://localhost:8000/ws/control-panel?device_token=$deviceToken'
);
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

**Modèles Dart à créer:**
```dart
enum AvailableMessageTypes {
  command,       // Envoyer une commande clavier
  typing,        // Taper du texte
  disconnect,    // Demander la déconnexion
  statusUpdate;  // Mise à jour de statut

  String toJson() => name;
}

class PayloadFormat {
  final AvailableCommand? command;      // La commande à exécuter
  final String? textToType;              // Texte à taper
  final String? message;                 // Message de statut

  PayloadFormat({
    this.command,
    this.textToType,
    this.message,
  });

  Map<String, dynamic> toJson() {
    return {
      'command': command?.value,
      'text_to_type': textToType,
      'message': message,
    };
  }
}

class ControlPanelWSMessage {
  final AvailableMessageTypes messageType;
  final PayloadFormat? payload;

  ControlPanelWSMessage({
    required this.messageType,
    this.payload,
  });

  // Sérialiser pour envoyer au serveur
  String toJsonString() {
    return jsonEncode({
      'message_type': messageType.name,
      'payload': payload?.toJson(),
    });
  }
}

// Commandes disponibles
enum AvailableCommand {
  // Navigation
  up('UP'),
  down('DOWN'),
  left('LEFT'),
  right('RIGHT'),
  enter('ENTER'),

  // Média/Son
  mute('MUTE'),
  volumeUp('VOLUME_UP'),
  volumeDown('VOLUME_DOWN'),

  // Clavier
  copy('COPY'),              // Ctrl+C
  paste('PASTE'),            // Ctrl+V
  selectAll('SELECT_ALL'),   // Ctrl+A
  altTab('ALT_TAB'),         // Alt+Tab

  // Présentation
  startPresentation('START_PRESENTATION'), // F5
  endPresentation('END_PRESENTATION');     // Esc

  final String value;
  const AvailableCommand(this.value);

  static AvailableCommand? fromString(String value) {
    try {
      return AvailableCommand.values.firstWhere((e) => e.value == value);
    } catch (_) {
      return null;
    }
  }
}
```

**Exemples de messages JSON à envoyer:**

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
    type: WssMessageType                      # "COMMAND" ou "NOTIFY"
    data: Union[OutControlPanelWSMessage, Notification]
```

**Modèles Dart à créer:**
```dart
enum WssMessageType {
  newChallenge('NEW_CHALLENGE'),
  authenticationSuccess('AUTHENTIFICATION_SUCCESS'),
  command('COMMAND'),
  notify('NOTIFY');

  final String value;
  const WssMessageType(this.value);

  static WssMessageType fromString(String value) {
    return values.firstWhere(
      (e) => e.value == value,
      orElse: () => notify,
    );
  }
}

class OutControlPanelWSMessage {
  final bool succes;                    // ⚠️ "succes" pas "success"
  final ControlPanelWSMessage? data;   // Message d'écho (optionnel)
  final String? error;                  // Message d'erreur (si succes=false)

  OutControlPanelWSMessage({
    required this.succes,
    this.data,
    this.error,
  });

  factory OutControlPanelWSMessage.fromJson(Map<String, dynamic> json) {
    return OutControlPanelWSMessage(
      succes: json['succes'] as bool? ?? false,
      data: json['data'] != null
          ? ControlPanelWSMessage.fromJson(json['data'])
          : null,
      error: json['error'] as String?,
    );
  }
}

class Notification {
  final String message;

  Notification({required this.message});

  factory Notification.fromJson(Map<String, dynamic> json) {
    return Notification(message: json['message'] as String? ?? '');
  }
}

class WsPayloadMessage {
  final WssMessageType type;
  final dynamic data; // OutControlPanelWSMessage ou Notification

  WsPayloadMessage({
    required this.type,
    required this.data,
  });

  factory WsPayloadMessage.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String? ?? '';
    final type = WssMessageType.fromString(typeStr);

    dynamic data;
    if (type == WssMessageType.command) {
      data = OutControlPanelWSMessage.fromJson(json['data'] ?? {});
    } else if (type == WssMessageType.notify) {
      data = Notification.fromJson(json['data'] ?? {});
    } else {
      data = json['data'];
    }

    return WsPayloadMessage(type: type, data: data);
  }
}
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

## Modèles Dart complets

### Fichier `lib/models/auth_models.dart`

```dart
import 'dart:convert';

// ========== AUTHENTIFICATION ==========

class VerifyAuthRequest {
  final String? challengeId;
  final String? pin;

  VerifyAuthRequest({
    this.challengeId,
    this.pin,
  });

  bool isValid() {
    return (challengeId != null && challengeId!.isNotEmpty) ||
           (pin != null && pin!.isNotEmpty);
  }

  Map<String, dynamic> toJson() => {
    'challenge_id': challengeId,
    'pin': pin,
  };

  String toJsonString() => jsonEncode(toJson());
}

class VerifyAuthResponse {
  final String deviceId;
  final String deviceToken;
  final String sessionToken;
  final DateTime sessionExpiresAt;

  VerifyAuthResponse({
    required this.deviceId,
    required this.deviceToken,
    required this.sessionToken,
    required this.sessionExpiresAt,
  });

  factory VerifyAuthResponse.fromJson(Map<String, dynamic> json) {
    return VerifyAuthResponse(
      deviceId: json['device_id'] as String,
      deviceToken: json['device_token'] as String,
      sessionToken: json['session_token'] as String,
      sessionExpiresAt: DateTime.parse(json['session_expires_at'] as String),
    );
  }

  bool isExpired() => DateTime.now().isAfter(sessionExpiresAt);
}

class ApiBaseResponse<T> {
  final bool ok;
  final T? result;
  final String? error;

  ApiBaseResponse({
    required this.ok,
    this.result,
    this.error,
  });

  factory ApiBaseResponse.fromJson(
    Map<String, dynamic> json,
    T Function(dynamic) fromJsonT,
  ) {
    return ApiBaseResponse(
      ok: json['ok'] as bool? ?? false,
      result: json['ok'] == true && json['result'] != null
          ? fromJsonT(json['result'])
          : null,
      error: json['error'] as String?,
    );
  }
}

enum AuthError {
  challengeUsed,
  unexistChallenge,
  invalidPin,
  unfoundPin,
  blockedPin,
  challengeTimeOut,
  unknownError,
}

// ========== WEBSOCKET CONTROL PANEL ==========

enum AvailableMessageTypes {
  command,
  typing,
  disconnect,
  statusUpdate;

  String toJson() => name;
}

enum AvailableCommand {
  up('UP'),
  down('DOWN'),
  left('LEFT'),
  right('RIGHT'),
  enter('ENTER'),
  mute('MUTE'),
  volumeUp('VOLUME_UP'),
  volumeDown('VOLUME_DOWN'),
  copy('COPY'),
  paste('PASTE'),
  selectAll('SELECT_ALL'),
  altTab('ALT_TAB'),
  startPresentation('START_PRESENTATION'),
  endPresentation('END_PRESENTATION');

  final String value;
  const AvailableCommand(this.value);

  static AvailableCommand? fromString(String value) {
    try {
      return AvailableCommand.values.firstWhere((e) => e.value == value);
    } catch (_) {
      return null;
    }
  }
}

class PayloadFormat {
  final AvailableCommand? command;
  final String? textToType;
  final String? message;

  PayloadFormat({
    this.command,
    this.textToType,
    this.message,
  });

  Map<String, dynamic> toJson() => {
    'command': command?.value,
    'text_to_type': textToType,
    'message': message,
  };

  factory PayloadFormat.fromJson(Map<String, dynamic> json) {
    return PayloadFormat(
      command: json['command'] != null
          ? AvailableCommand.fromString(json['command'] as String)
          : null,
      textToType: json['text_to_type'] as String?,
      message: json['message'] as String?,
    );
  }
}

class ControlPanelWSMessage {
  final AvailableMessageTypes messageType;
  final PayloadFormat? payload;

  ControlPanelWSMessage({
    required this.messageType,
    this.payload,
  });

  String toJsonString() => jsonEncode({
    'message_type': messageType.name,
    'payload': payload?.toJson(),
  });

  factory ControlPanelWSMessage.fromJson(Map<String, dynamic> json) {
    return ControlPanelWSMessage(
      messageType: AvailableMessageTypes.values.firstWhere(
        (e) => e.name == json['message_type'],
        orElse: () => AvailableMessageTypes.disconnect,
      ),
      payload: json['payload'] != null
          ? PayloadFormat.fromJson(json['payload'])
          : null,
    );
  }
}

enum WssMessageType {
  newChallenge('NEW_CHALLENGE'),
  authenticationSuccess('AUTHENTIFICATION_SUCCESS'),
  command('COMMAND'),
  notify('NOTIFY');

  final String value;
  const WssMessageType(this.value);

  static WssMessageType fromString(String value) {
    return values.firstWhere(
      (e) => e.value == value,
      orElse: () => notify,
    );
  }
}

class OutControlPanelWSMessage {
  final bool succes;
  final ControlPanelWSMessage? data;
  final String? error;

  OutControlPanelWSMessage({
    required this.succes,
    this.data,
    this.error,
  });

  factory OutControlPanelWSMessage.fromJson(Map<String, dynamic> json) {
    return OutControlPanelWSMessage(
      succes: json['succes'] as bool? ?? false,
      data: json['data'] != null
          ? ControlPanelWSMessage.fromJson(json['data'])
          : null,
      error: json['error'] as String?,
    );
  }
}

class Notification {
  final String message;

  Notification({required this.message});

  factory Notification.fromJson(Map<String, dynamic> json) {
    return Notification(message: json['message'] as String? ?? '');
  }
}

class WsPayloadMessage {
  final WssMessageType type;
  final dynamic data;

  WsPayloadMessage({
    required this.type,
    required this.data,
  });

  factory WsPayloadMessage.fromJson(Map<String, dynamic> json) {
    final typeStr = json['type'] as String? ?? '';
    final type = WssMessageType.fromString(typeStr);

    dynamic data;
    if (type == WssMessageType.command) {
      data = OutControlPanelWSMessage.fromJson(json['data'] ?? {});
    } else if (type == WssMessageType.notify) {
      data = Notification.fromJson(json['data'] ?? {});
    } else {
      data = json['data'];
    }

    return WsPayloadMessage(type: type, data: data);
  }
}
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

### Gestion côté Dart

```dart
String getErrorMessage(AuthError error) {
  switch (error) {
    case AuthError.challengeUsed:
      return 'Ce QR code a déjà été utilisé. Veuillez rafraîchir.';
    case AuthError.unexistChallenge:
      return 'Le QR code n\'est pas valide.';
    case AuthError.challengeTimeOut:
      return 'Le QR code a expiré. Veuillez rafraîchir.';
    case AuthError.invalidPin:
      return 'Le PIN saisi est incorrect.';
    case AuthError.unfoundPin:
      return 'Le PIN n\'existe pas.';
    case AuthError.blockedPin:
      return 'Trop de tentatives. Attendez 5 minutes.';
    default:
      return 'Erreur d\'authentification.';
  }
}

AuthError parseAuthError(String errorMessage) {
  if (errorMessage.contains('CHALLENGE_USED')) return AuthError.challengeUsed;
  if (errorMessage.contains('UNEXIST_CHALLENGE')) return AuthError.unexistChallenge;
  if (errorMessage.contains('INVALID_PIN')) return AuthError.invalidPin;
  if (errorMessage.contains('UNFOUND_PIN')) return AuthError.unfoundPin;
  if (errorMessage.contains('BLOCKED_PIN')) return AuthError.blockedPin;
  if (errorMessage.contains('CHALLENGE_TIME_OUT')) return AuthError.challengeTimeOut;
  return AuthError.unknownError;
}
```

---

## Points clés d'implémentation

### ✅ À FAIRE

1. **Validation stricte du PIN**
   - Vérifier que le PIN fait exactement 6 chiffres
   - Accepter uniquement des caractères numériques
   - Afficher un message d'erreur explicite

2. **Gestion du device_token**
   - Toujours le passer en paramètre d'URL pour le WebSocket
   - Ne jamais l'inclure dans le body de la requête
   - Le stocker de manière sécurisée (SharedPreferences chiffré)

3. **État de connexion**
   - Afficher un indicateur visuel de connexion WebSocket
   - Gérer les déconnexions inattendues
   - Implémenter un système de reconnexion automatique

4. **Timeout et limites**
   - PIN valable 5 minutes (afficher le timer)
   - Challenge valable 5 minutes
   - Timeout HTTP de 10 secondes
   - Retry avec backoff exponentiel en cas d'erreur réseau

### ❌ À ÉVITER

1. Ne pas réutiliser un token expiré
2. Ne pas envoyer de PIN après 3 tentatives échouées
3. Ne pas oublier le device_token en paramètre WebSocket
4. Ne pas stocker les tokens en clair sans chiffrement
5. Ne pas afficher les UUIDs bruts à l'utilisateur
6. Ne pas laisser la connexion WebSocket ouverte sans heartbeat
7. Ne pas ignorer les exceptions WebSocket

### 🔐 Sécurité

```dart
// Stockage sécurisé des tokens
// ✅ BON - Chiffré
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const secureStorage = FlutterSecureStorage();
await secureStorage.write(key: 'device_token', value: token);

// ❌ MAUVAIS - En clair
final prefs = await SharedPreferences.getInstance();
prefs.setString('device_token', token);  // Visible en clair!
```

### 📊 Flux complet en Dart

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

// 1. Appeler /auth/verify
final request = VerifyAuthRequest(
  challengeId: scannedQRCode,
  pin: null,
);

final response = await http.post(
  Uri.parse('http://[SERVER]/auth/verify'),
  headers: {'Content-Type': 'application/json'},
  body: request.toJsonString(),
).timeout(const Duration(seconds: 10));

final jsonData = jsonDecode(response.body) as Map<String, dynamic>;
final apiResponse = ApiBaseResponse<VerifyAuthResponse>.fromJson(
  jsonData,
  (json) => VerifyAuthResponse.fromJson(json),
);

if (apiResponse.ok && apiResponse.result != null) {
  // 2. Stocker les tokens
  final deviceToken = apiResponse.result!.deviceToken;
  await secureStorage.write(key: 'device_token', value: deviceToken);

  // 3. Connecter au WebSocket
  final ws = await WebSocket.connect(
    'ws://[SERVER]/ws/control-panel?device_token=$deviceToken',
  );

  // 4. Écouter les messages
  ws.listen(
    (message) {
      final jsonMsg = jsonDecode(message) as Map<String, dynamic>;
      final wsMessage = WsPayloadMessage.fromJson(jsonMsg);

      if (wsMessage.type == WssMessageType.command) {
        final response = wsMessage.data as OutControlPanelWSMessage;
        if (response.succes) {
          // Commande exécutée ✅
        } else {
          // Erreur: response.error
        }
      }
    },
    onError: (error) {
      // Gestion erreur WebSocket
    },
    onDone: () {
      // WebSocket fermé
    },
  );

  // 5. Envoyer une commande
  final message = ControlPanelWSMessage(
    messageType: AvailableMessageTypes.command,
    payload: PayloadFormat(command: AvailableCommand.up),
  );
  ws.add(message.toJsonString());

  // 6. Déconnecter proprement
  final disconnectMsg = ControlPanelWSMessage(
    messageType: AvailableMessageTypes.disconnect,
    payload: null,
  );
  ws.add(disconnectMsg.toJsonString());
  await ws.close();
} else {
  // Afficher l'erreur: apiResponse.error
  final error = parseAuthError(apiResponse.error ?? '');
  showError(getErrorMessage(error));
}
```

---

## Résumé des étapes critiques

| Étape | Action | Validation |
|-------|--------|-----------|
| 1 | POST `/auth/verify` | `ok: true` et `result` non-null |
| 2 | Récupérer `device_token` | Non-null et non-vide |
| 3 | Ouvrir WebSocket avec token | Connexion établie |
| 4 | Envoyer commandes | Format JSON strict respecté |
| 5 | Traiter réponses | Vérifier `data.succes` et `data.error` |
| 6 | Déconnecter proprement | Message `disconnect` puis `close()` |

---

## Checklist avant production

- [ ] Validation du PIN (6 chiffres, numériques uniquement)
- [ ] Gestion complète des erreurs `/auth/verify`
- [ ] device_token stocké de manière sécurisée
- [ ] device_token passé en paramètre d'URL WebSocket
- [ ] Timeout HTTP (10 secondes)
- [ ] Timeout WebSocket implémenté
- [ ] Reconnexion automatique en cas de déconnexion
- [ ] Affichage d'indicateurs de connexion à l'utilisateur
- [ ] Messages d'erreur clairs et en français
- [ ] Gestion des tokens expirés
- [ ] No hardcoded server URLs
- [ ] Logs appropriés (sans afficher les tokens)

