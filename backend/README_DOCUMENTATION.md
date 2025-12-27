# 📚 Documentation du Workflow d'Authentification

Bienvenue dans la documentation du système d'authentification de **RemoteKeyboardController**. Ce dossier contient deux guides complets destinés aux développeurs front-end.

---

## 📖 Guide pour Web React

**Fichier :** `DOCUMENTATION_REACT_WEB.md`

### Contenu
- ✅ Vue d'ensemble complète du workflow
- ✅ Route POST `/auth/verify` - Structure exacte des requêtes/réponses
- ✅ WebSocket `/ws/control-panel` - Communication bidirectionnelle
- ✅ Tous les codes d'erreur et leur signification
- ✅ Points clés d'implémentation (À FAIRE / À ÉVITER)
- ✅ Exemple de flux complet en JavaScript

### Sections principales
1. Aperçu du workflow
2. Route POST `/auth/verify`
3. WebSocket `/ws/control-panel`
4. Structure complète des données
5. Gestion des erreurs
6. Points clés d'implémentation

---

## 📱 Guide pour Mobile Flutter

**Fichier :** `DOCUMENTATION_FLUTTER_MOBILE.md`

### Contenu
- ✅ Vue d'ensemble du workflow mobile
- ✅ Route POST `/auth/verify` - Structure exacte des requêtes/réponses
- ✅ WebSocket `/ws/control-panel` - Communication bidirectionnelle
- ✅ **Modèles Dart complets et prêts à copier/coller**
- ✅ Tous les codes d'erreur et leur gestion
- ✅ Points clés d'implémentation (À FAIRE / À ÉVITER)
- ✅ Exemple de flux complet en Dart

### Sections principales
1. Aperçu du workflow
2. Route POST `/auth/verify`
3. WebSocket `/ws/control-panel`
4. Modèles Dart complets (prêts à utiliser)
5. Gestion des erreurs
6. Points clés d'implémentation

---

## 🔑 Points Clés Communs

### 1️⃣ Route POST `/auth/verify`

**URL:** `POST http://[SERVER]/auth/verify`

**Requête:**
```json
{
  "challenge_id": "UUID (optionnel, du QR code)"  OU
  "pin": "string (optionnel, 6 chiffres)"
}
```
⚠️ **Au moins UN des deux doit être fourni**

**Réponse (succès):**
```json
{
  "ok": true,
  "result": {
    "device_id": "UUID",
    "device_token": "string",        // À utiliser pour le WebSocket
    "session_token": "string",
    "session_expires_at": "ISO 8601"
  }
}
```

**Réponse (erreur):**
```json
{
  "ok": false,
  "error": "CHALLENGE_USED | UNEXIST_CHALLENGE | INVALID_PIN | BLOCKED_PIN | UNFOUND_PIN | CHALLENGE_TIME_OUT"
}
```

### 2️⃣ WebSocket `/ws/control-panel`

**URL:** `ws://[SERVER]/ws/control-panel?device_token=[YOUR_DEVICE_TOKEN]`

⚠️ **Le device_token DOIT être passé en paramètre d'URL**

**Message à envoyer:**
```json
{
  "message_type": "command" | "typing" | "disconnect",
  "payload": {
    "command": "UP" | "DOWN" | "COPY" | ... (voir liste complète)
    "text_to_type": "texte (optionnel)"
  }
}
```

**Message reçu:**
```json
{
  "type": "COMMAND" | "NOTIFY",
  "data": {
    "succes": true/false,        // ⚠️ "succes" pas "success"
    "data": { ... },              // Écho du message envoyé
    "error": "message d'erreur si succes=false"
  }
}
```

---

## 📋 Commandes Disponibles

### Navigation
- `UP` - Flèche haut
- `DOWN` - Flèche bas
- `LEFT` - Flèche gauche
- `RIGHT` - Flèche droite
- `ENTER` - Entrée

### Média
- `MUTE` - Muet
- `VOLUME_UP` - Volume +
- `VOLUME_DOWN` - Volume -

### Clavier
- `COPY` - Ctrl+C
- `PASTE` - Ctrl+V
- `SELECT_ALL` - Ctrl+A
- `ALT_TAB` - Alt+Tab

### Présentation
- `START_PRESENTATION` - F5
- `END_PRESENTATION` - Esc

---

## ⚠️ Erreurs Possibles

| Code | Signification | Action |
|------|---------------|--------|
| `CHALLENGE_USED` | Challenge déjà utilisé | Rafraîchir, scanner nouveau QR |
| `UNEXIST_CHALLENGE` | QR code inexistant | Rafraîchir, scanner nouveau QR |
| `CHALLENGE_TIME_OUT` | QR code expiré (> 5 min) | Rafraîchir, scanner nouveau QR |
| `INVALID_PIN` | PIN incorrect | Vérifier et resaisir |
| `UNFOUND_PIN` | PIN inexistant | Vérifier et resaisir |
| `BLOCKED_PIN` | Trop d'essais (> 3) | Attendre 5 minutes |

---

## 🔐 Bonnes Pratiques de Sécurité

✅ **À FAIRE:**
- Stocker les tokens de manière sécurisée (sessionStorage/SecureStorage)
- Valider le PIN (6 chiffres, numériques uniquement)
- Passer le device_token en paramètre d'URL pour le WebSocket
- Gérer les tokens expirés
- Implémenter un timeout HTTP (10 secondes)
- Afficher des messages d'erreur clairs à l'utilisateur

❌ **À ÉVITER:**
- Ne pas réutiliser un token expiré
- Ne pas stocker les tokens en localStorage/SharedPreferences sans chiffrement
- Ne pas envoyer de PIN après 3 tentatives échouées
- Ne pas oublier le device_token en paramètre WebSocket
- Ne pas laisser la connexion WebSocket ouverte sans heartbeat
- Ne pas afficher les UUIDs bruts à l'utilisateur

---

## 📞 Questions Fréquentes

### Q: Où récupérer le `challenge_id` ?
**R:** Le `challenge_id` est contenu dans le QR code que vous scannez. Le serveur génère un nouveau QR code toutes les 5 minutes via le WebSocket d'attente. Vous devez décoder le QR pour extraire l'UUID.

### Q: Pourquoi il y a "succes" au lieu de "success" dans la réponse WebSocket ?
**R:** C'est une typo du backend conservée pour compatibilité. Vérifiez bien le champ `succes` (avec un seul 's').

### Q: Combien de temps sont valides les tokens ?
**R:** 
- Challenge: 5 minutes
- PIN: 5 minutes
- device_token: 1 heure
- session_token: 1 heure

### Q: Que faire si le WebSocket se déconnecte inopinément ?
**R:** Implémenter un système de reconnexion avec backoff exponentiel. Afficher un message à l'utilisateur et proposer une reconnexion manuelle.

### Q: Puis-je conserver le device_token pour des connexions ultérieures ?
**R:** Oui, le device_token est persistant durant son heure de validité. Vous pouvez le réutiliser pour vous reconnecter au WebSocket control-panel.

---

## 🚀 Prochaines Étapes

1. **Pour React Web:**
   - Lire `DOCUMENTATION_REACT_WEB.md`
   - Implémenter un hook personnalisé pour `/auth/verify`
   - Implémenter un hook personnalisé pour le WebSocket control-panel
   - Tester avec des QR codes et des PINs

2. **Pour Flutter Mobile:**
   - Lire `DOCUMENTATION_FLUTTER_MOBILE.md`
   - Copier les modèles Dart fournis
   - Implémenter les services (AuthService, ControlPanelService)
   - Tester avec des QR codes et des PINs

---

## 📝 Notes Techniques

### Schémas Pydantic du Backend
Tous les schémas utilisés par le backend sont documentés dans :
- `app/schemas/auth_schema.py` - Schémas d'authentification
- `app/schemas/control_panel_ws_schema.py` - Schémas WebSocket control-panel
- `app/schemas/admin_panel_ws_schema.py` - Schémas généraux WebSocket
- `app/schemas/base_schema.py` - Schéma de base pour les réponses API

### Routes Backend
- **HTTP:** `/auth/verify` - Vérification de l'authentification
- **WebSocket:** `/ws/waiting` - Réception des challenges/PINs
- **WebSocket:** `/ws/control-panel` - Envoi de commandes

### Managers Backend
- `ChallengeManager` - Gère les challenges (création, validation, marquage comme utilisé)
- `PinManager` - Gère les PINs (création, validation, blocage après 3 essais)
- `DeviceManager` - Gère la création des tokens

---

## 📞 Support

Si vous avez des questions ou des problèmes avec l'intégration :
1. Vérifiez les sections "Points clés d'implémentation"
2. Consultez la section "Gestion des erreurs"
3. Révisez les exemples de flux complets fournis

Bonne implémentation! 🎉

