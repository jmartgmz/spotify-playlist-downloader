# Spotify API Setup Instructions

To use this script, you need Spotify API credentials. Follow these steps:

1. Go to the Spotify Developer Dashboard: https://developer.spotify.com/dashboard
2. Log in with your Spotify account.
3. Click "Create an App".
4. Enter an app name and description (anything you like).
5. After the app is created, click on it to view details.
6. Copy the "Client ID" and "Client Secret".
7. In your terminal, set these as environment variables:
   
   ```bash
   export SPOTIFY_CLIENT_ID='your_client_id_here'
   export SPOTIFY_CLIENT_SECRET='your_client_secret_here'
   ```
   Or, you can add them to your shell profile (e.g., `~/.bashrc` or `~/.zshrc`).

8. Restart your terminal or source your profile if you added them there.

9. Now you can run the script and it will use your credentials.

---

**Note:**
- Your credentials are private. Do not share them.
- You only need to do this setup once per machine.
