# ✅ CHECKLIST D'IMPLÉMENTATION

Ce document récapitule les points critiques pour l'implémentation du workflow d'authentification. Utilisez cette checklist pour vous assurer que votre intégration est complète et correcte.

---

## 📋 Route POST `/auth/verify`

### Requête (Client → Serveur)

- [ ] Méthode: **POST** (pas GET, PUT, DELETE, etc.)
- [ ] URL: `http://[SERVER]/auth/verify`
- [ ] Header: `Content-Type: application/json`
- [ ] Body contient **AU MOINS** un des deux champs:
  - [ ] `challenge_id`: UUID (string) du QR code scanné
  - [ ] `pin`: String de 6 chiffres numériques
- [ ] Validation côté client avant envoi:
  - [ ] PIN doit faire exactement 6 chiffres si fourni
  - [ ] Challenge_id doit être un UUID valide si fourni
  - [ ] Les deux ne peuvent pas être null en même temps

### Réponse (Serveur → Client)

- [ ] Vérifier le champ `ok`:
  - [ ] Si `ok: true` → Succès, utiliser `result`
  - [ ] Si `ok: false` → Erreur, utiliser `error`
- [ ] En cas de succès:
  - [ ] `result.device_id` présent et non-null
  - [ ] `result.device_token` présent et non-null ⚠️ **À stocker immédiatement**
  - [ ] `result.session_token` présent et non-null
  - [ ] `result.session_expires_at` en format ISO 8601
- [ ] En cas d'erreur:
  - [ ] `error` contient un message d'erreur
  - [ ] Parser le message pour afficher une UI appropriée
  - [ ] Code d'erreur reconnu parmi: `CHALLENGE_USED`, `UNEXIST_CHALLENGE`, `INVALID_PIN`, `BLOCKED_PIN`, `UNFOUND_PIN`, `CHALLENGE_TIME_OUT`

### Gestion des erreurs

- [ ] `CHALLENGE_USED`: Afficher "Ce QR code a déjà été utilisé"
- [ ] `UNEXIST_CHALLENGE`: Afficher "Le QR code n'est pas valide"
- [ ] `CHALLENGE_TIME_OUT`: Afficher "Le QR code a expiré (> 5 min)"
- [ ] `INVALID_PIN`: Afficher "Le PIN saisi est incorrect"
- [ ] `UNFOUND_PIN`: Afficher "Le PIN n'existe pas"
- [ ] `BLOCKED_PIN`: Afficher "Trop de tentatives, attendez 5 minutes"
- [ ] Implémenter un retry avec backoff exponentiel
- [ ] Timeout HTTP: 10 secondes

---

## 🔌 WebSocket `/ws/control-panel`

### Connexion

- [ ] URL: `ws://[SERVER]/ws/control-panel?device_token=[TOKEN]`
- [ ] **⚠️ CRITIQUE:** device_token passé en paramètre d'URL, PAS dans le body
- [ ] device_token provient de la réponse `/auth/verify`
- [ ] État de connexion: `readyState === OPEN` (1 en JavaScript)
- [ ] Afficher un indicateur visuel de connexion à l'utilisateur
- [ ] Gérer les déconnexions inattendues avec message à l'utilisateur

### Messages à envoyer (Client → Serveur)

**Format général:**
- [ ] Structure JSON stricte:
  ```json
  {
    "message_type": "command" | "typing" | "disconnect",
    "payload": { /* contenu selon type */ }
  }
  ```

**Type: `command`**
- [ ] `payload.command` doit être l'une des clés disponibles
- [ ] Clés valides: `UP`, `DOWN`, `LEFT`, `RIGHT`, `ENTER`, `MUTE`, `VOLUME_UP`, `VOLUME_DOWN`, `COPY`, `PASTE`, `SELECT_ALL`, `ALT_TAB`, `START_PRESENTATION`, `END_PRESENTATION`
- [ ] `payload.command` ne doit pas être null
- [ ] `payload.text_to_type` et `payload.message` doivent être null

**Type: `typing`**
- [ ] `payload.text_to_type` contient le texte à taper
- [ ] `payload.text_to_type` ne doit pas être null
- [ ] `payload.command` et `payload.message` doivent être null

**Type: `disconnect`**
- [ ] `payload` doit être null ou vide
- [ ] Envoyer avant d'appeler `close()` sur la connexion

### Messages reçus (Serveur → Client)

**Format général:**
- [ ] Structure JSON:
  ```json
  {
    "type": "COMMAND" | "NOTIFY",
    "data": { /* contenu selon type */ }
  }
  ```

**Type: `COMMAND`**
- [ ] `data.succes` est un booléen (⚠️ **attention: "succes" pas "success"**)
- [ ] Si `succes: true`:
  - [ ] `data.data` contient l'écho du message envoyé
  - [ ] `data.error` est null
  - [ ] ✅ Commande exécutée avec succès
- [ ] Si `succes: false`:
  - [ ] `data.data` est null
  - [ ] `data.error` contient le message d'erreur
  - [ ] ❌ Afficher le message d'erreur à l'utilisateur

**Type: `NOTIFY`**
- [ ] `data.message` contient un message de notification
- [ ] Afficher à l'utilisateur ou logger selon la priorité

### Gestion des erreurs WebSocket

- [ ] Mettre en place un `onError` handler
- [ ] Mettre en place un `onClose`/`onDone` handler
- [ ] Reconnexion automatique avec backoff exponentiel
- [ ] Ne pas spammer les reconnexions (max 5 tentatives par minute)
- [ ] Afficher un indicateur "Reconnexion en cours..." à l'utilisateur

---

## 🔐 Stockage et Sécurité des Tokens

### React Web

- [ ] **sessionStorage** pour les tokens (durée de session)
  - [ ] `sessionStorage.setItem('device_token', token)`
  - [ ] `sessionStorage.getItem('device_token')`
  - [ ] ❌ Ne pas utiliser `localStorage` sans chiffrement!

- [ ] Tokens supprimés à la fermeture du navigateur
- [ ] Ne pas logger les tokens en production
- [ ] Ne jamais envoyer les tokens en URL (sauf device_token en param pour WebSocket, c'est permis)

### Flutter Mobile

- [ ] **flutter_secure_storage** pour les tokens
  - [ ] `await secureStorage.write(key: 'device_token', value: token)`
  - [ ] `await secureStorage.read(key: 'device_token')`
  - [ ] ❌ Ne pas utiliser SharedPreferences sans chiffrement!

- [ ] Tokens supprimés à la déconnexion
- [ ] Ne pas logger les tokens en production
- [ ] Ne jamais envoyer les tokens en URL (sauf device_token en param pour WebSocket)

---

## ⏱️ Gestion des Timeouts et Expirations

- [ ] **Challenge:** 5 minutes (afficher un timer sur l'écran)
- [ ] **PIN:** 5 minutes (afficher un timer sur l'écran)
- [ ] **device_token:** 1 heure
- [ ] **session_token:** 1 heure
- [ ] **HTTP timeout:** 10 secondes (fallback)
- [ ] **WebSocket timeout:** Implémenter un heartbeat si pas de message pendant 30 secondes
- [ ] Vérifier l'expiration avant d'utiliser un token
- [ ] Rediriger vers l'authentification si token expiré

---

## 🎯 Validation et Limites

### PIN
- [ ] Exactement 6 chiffres
- [ ] Uniquement des caractères numériques (0-9)
- [ ] Maximum 3 tentatives avant blocage
- [ ] Blocage de 5 minutes après 3 tentatives

### Challenge
- [ ] UUID valide (format correct)
- [ ] Non réutilisable (1 seule utilisation)
- [ ] Valable 5 minutes maximum

### WebSocket
- [ ] Maximum 1 connexion par device_token à la fois
- [ ] Pas de commandes pendant que le WebSocket est en cours de reconnexion
- [ ] Vérifier le statut de la connexion avant d'envoyer des commandes

---

## 🖥️ Indicateurs Visuels et UX

- [ ] Indicateur de connexion WebSocket (couleur verte = connecté)
- [ ] Indicateur de connexion en cours de chargement (spinner)
- [ ] Indicateur de déconnexion ou erreur (couleur rouge)
- [ ] Timer affichant le temps restant pour le challenge/PIN
- [ ] Message d'erreur clair et en français
- [ ] Bouton "Réessayer" en cas d'erreur
- [ ] Bouton "Déconnecter" pour fermer la session
- [ ] Confirmation avant de fermer une connexion active

---

## 🧪 Tests Critiques

- [ ] ✅ Authentification par QR code valide
- [ ] ✅ Authentification par PIN correct
- [ ] ✅ Authentification par PIN incorrect (3 tentatives)
- [ ] ✅ QR code expiré (> 5 min)
- [ ] ✅ QR code déjà utilisé
- [ ] ✅ WebSocket se connecte après authentification réussie
- [ ] ✅ Envoi de commande "UP" fonctionne
- [ ] ✅ Envoi de texte fonctionne
- [ ] ✅ Réception des confirmations de commande
- [ ] ✅ Gestion de la déconnexion inopinée
- [ ] ✅ Reconnexion automatique après déconnexion
- [ ] ✅ Token stocké de manière sécurisée
- [ ] ✅ Token utilisé correctement pour le WebSocket
- [ ] ✅ Pas de fuite de token dans les logs

---

## 📊 Monitoring et Logs

- [ ] Logs d'erreur avec `try/catch` appropriés
- [ ] ❌ Ne pas logger les tokens, device_id, ou données sensibles
- [ ] ✅ Logger l'état de la connexion (connecté, déconnecté, erreur)
- [ ] ✅ Logger les erreurs d'authentification (code d'erreur seulement, pas le message complet)
- [ ] ✅ Logger les timeouts et reconnexions
- [ ] Monitoring des performances (temps de réponse)
- [ ] Alerte si trop de réessais échoués (> 5 fois)

---

## 📱 Spécifique à Flutter

- [ ] Modèles Dart créés (VerifyAuthRequest, VerifyAuthResponse, etc.)
- [ ] Services créés (AuthService, ControlPanelService)
- [ ] Gestion des futures et streams correcte
- [ ] Pas de memory leaks avec les WebSocket streams
- [ ] Dispose des ressources proprement dans `dispose()`
- [ ] Tests unitaires pour la sérialisation/désérialisation JSON
- [ ] Gestion des notifications (push, local)

---

## 🌐 Spécifique à React

- [ ] Hooks personnalisés créés (useAuthVerify, useWebSocket, etc.)
- [ ] Context ou State Management pour les tokens
- [ ] Cleanup des effects (`useEffect` cleanup)
- [ ] Pas de memory leaks avec les WebSocket event listeners
- [ ] Tests unitaires pour les composants
- [ ] Error boundaries pour l'authentification
- [ ] Gestion du routing après authentification

---

## 🚀 Avant la production

- [ ] Revue de code complet
- [ ] Tests de charge (100+ connexions simultanées)
- [ ] Tests de sécurité (injection, CSRF, XSS, etc.)
- [ ] Certificat SSL/TLS en place (HTTPS/WSS)
- [ ] Variables d'environnement pour les URLs
- [ ] Configuration des CORS appropriée
- [ ] Logs de production sans informations sensibles
- [ ] Monitoring en place (uptimes, erreurs, performances)
- [ ] Plan de rollback en cas de problème

---

## 📞 Ressources

| Ressource | Lien |
|-----------|------|
| Documentation React | `DOCUMENTATION_REACT_WEB.md` |
| Documentation Flutter | `DOCUMENTATION_FLUTTER_MOBILE.md` |
| Vue d'ensemble | `README_DOCUMENTATION.md` |
| Schémas Backend | `app/schemas/auth_schema.py`, `app/schemas/control_panel_ws_schema.py` |

---

**Dernière mise à jour:** 2024-12-21

**Status:** ✅ Complet et prêt pour l'implémentation

