# Big Data Engineering – Shopping App MVP Blueprint

Dieses Repository enthält jetzt:
- MVP-Spezifikation (`docs/mvp_architecture.md`)
- laufbares Backend-Setup (`backend/`)
- Expo Mobile-Setup (`mobile/`)

## Backend starten
```bash
cd /workspace/Big_Data_Engineering/backend
npm install
npm run dev
```

Health-Checks:
```bash
curl http://127.0.0.1:3000/health
curl http://127.0.0.1:3000/v1/health
```

## Mobile starten (Expo)
```bash
cd /workspace/Big_Data_Engineering/mobile
npm install
EXPO_PUBLIC_API_BASE=http://<DEINE_LAN_IP>:3000 npm run start
```

### IP/Device Hinweis
- Auf **Android Emulator** nutze meist: `http://10.0.2.2:3000`
- Auf **iOS Simulator** nutze: `http://127.0.0.1:3000`
- Auf **physischem Gerät** muss `EXPO_PUBLIC_API_BASE` auf deine **LAN-IP** zeigen, z. B. `http://192.168.178.25:3000`
- Backend muss mit `0.0.0.0` gebunden sein (ist in `backend/src/index.ts` so konfiguriert).
