# SPT Forge Discord Bot

Bot, der neue Mods von [sp-mod.com](https://sp-mod.com) automatisch in einen Discord-Channel postet.

## Einrichtung

1. **Discord Bot erstellen**
   - Gehe zu https://discord.com/developers/applications
   - Neue Application → Bot → Token kopieren
   - Bot zu deinem Server einladen (Permission: Send Messages, Embed Links)

2. **Channel-ID holen**
   - Discord → Einstellungen → Erweitert → Entwicklermodus aktivieren
   - Rechtsklick auf den Channel → ID kopieren

3. **Bot starten**
   ```bash
   pip install -r requirements.txt
   export DISCORD_TOKEN="dein_token"
   export CHANNEL_ID="123456789012345678"
   python forge_discord_bot.py
   ```

## Konfiguration

| Variable | Beschreibung | Default |
|----------|--------------|---------|
| `DISCORD_TOKEN` | Bot-Token | — |
| `CHANNEL_ID` | Ziel-Channel-ID | — |
| `POLL_INTERVAL` | Abfrageintervall in Minuten | 10 |

## Hinweise

- Der Bot merkt sich bereits gesehene Mods in `seen_mods.json`.
- Beim ersten Start werden die aktuell neuesten Mods als „gesehen“ markiert (keine Flut).
- Die API von sp-mod.com ist öffentlich und braucht keinen Key.
