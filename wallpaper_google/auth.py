"""Login con Google (OAuth para apps de escritorio)."""

import os
import sys

from google.auth.transport.requests import AuthorizedSession, Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from . import paths

SCOPES = ["https://www.googleapis.com/auth/photospicker.mediaitems.readonly"]


def _save(creds: Credentials) -> None:
    paths.TOKEN_FILE.write_text(creds.to_json())
    os.chmod(paths.TOKEN_FILE, 0o600)


def get_credentials(interactive: bool = True) -> Credentials:
    paths.ensure_dirs()
    creds = None
    if paths.TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(paths.TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save(creds)
        return creds
    if not interactive:
        sys.exit("No hay sesión de Google. Ejecuta: wallpaper-google login")
    if not paths.CLIENT_SECRET.exists():
        sys.exit(
            f"Falta {paths.CLIENT_SECRET}\n"
            "Descarga el JSON del cliente OAuth (tipo 'App de escritorio') "
            "desde Google Cloud Console y cópialo ahí. Ver README."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(paths.CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True)
    _save(creds)
    return creds


def session(interactive: bool = True) -> AuthorizedSession:
    return AuthorizedSession(get_credentials(interactive))
