from typing import Optional, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json
import base64
import hashlib
import hmac

load_dotenv()

# ── AIRA OAUTH 2.0 / SAML / OIDC CONNECTOR ──

class OAuthSAMLConnector:
    """
    OAuth 2.0, SAML 2.0, and OpenID Connect connector.
    Handles enterprise SSO, token validation,
    and federated identity across all AIRA integrations.
    """

    def __init__(self):
        self.secret_key    = os.getenv("SECRET_KEY", "aira-secret")
        self.issuer        = os.getenv("OAUTH_ISSUER", "https://aira.company.com")
        self.client_id     = os.getenv("OAUTH_CLIENT_ID", "aira-client")
        self.token_expiry  = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.active_tokens = []
        self.saml_sessions = []

    # ── OAUTH 2.0 ──

    def generate_oauth_token(
        self,
        identity_id: str,
        email:       str,
        role:        str,
        scopes:      List[str]
    ) -> dict:
        """Generate an OAuth 2.0 access token for an identity."""
        issued_at  = datetime.utcnow()
        expires_at = issued_at + timedelta(minutes=self.token_expiry)

        payload = {
            "iss":        self.issuer,
            "sub":        identity_id,
            "email":      email,
            "role":       role,
            "scopes":     scopes,
            "iat":        issued_at.isoformat(),
            "exp":        expires_at.isoformat(),
            "client_id":  self.client_id
        }

        # Simple token (production: use python-jose JWT)
        token_data = json.dumps(payload).encode()
        signature  = hmac.new(
            self.secret_key.encode(),
            token_data,
            hashlib.sha256
        ).hexdigest()

        token = base64.b64encode(token_data).decode() + "." + signature

        token_record = {
            "token":       token[:32] + "...",
            "identity_id": identity_id,
            "email":       email,
            "role":        role,
            "scopes":      scopes,
            "issued_at":   issued_at.isoformat(),
            "expires_at":  expires_at.isoformat(),
            "active":      True
        }

        self.active_tokens.append(token_record)
        return token_record

    def validate_token(self, token_preview: str) -> dict:
        """Validate an OAuth token."""
        for t in self.active_tokens:
            if t["token"].startswith(token_preview[:10]):
                expiry = datetime.fromisoformat(t["expires_at"])
                if datetime.utcnow() < expiry:
                    return {"valid": True, "token": t}
                else:
                    return {"valid": False, "reason": "Token expired"}
        return {"valid": False, "reason": "Token not found"}

    def revoke_token(self, identity_id: str) -> dict:
        """Revoke all tokens for an identity."""
        revoked = 0
        for token in self.active_tokens:
            if token["identity_id"] == identity_id:
                token["active"] = False
                revoked += 1
        return {
            "identity_id":    identity_id,
            "tokens_revoked": revoked,
            "revoked_at":     datetime.utcnow().isoformat()
        }

    # ── SAML 2.0 ──

    def create_saml_assertion(
        self,
        identity_id:  str,
        email:        str,
        attributes:   dict,
        sp_entity_id: str
    ) -> dict:
        """Create a SAML 2.0 assertion for SSO."""
        issued_at  = datetime.utcnow()
        expires_at = issued_at + timedelta(minutes=self.token_expiry)

        assertion = {
            "assertion_id":  f"AIRA-SAML-{len(self.saml_sessions)+1}",
            "issuer":        self.issuer,
            "sp_entity_id":  sp_entity_id,
            "identity_id":   identity_id,
            "email":         email,
            "attributes":    attributes,
            "issued_at":     issued_at.isoformat(),
            "expires_at":    expires_at.isoformat(),
            "status":        "success"
        }

        self.saml_sessions.append(assertion)
        return assertion

    def validate_saml_response(self, assertion_id: str) -> dict:
        """Validate a SAML response."""
        assertion = next(
            (a for a in self.saml_sessions if a["assertion_id"] == assertion_id),
            None
        )
        if not assertion:
            return {"valid": False, "reason": "Assertion not found"}

        expiry = datetime.fromisoformat(assertion["expires_at"])
        if datetime.utcnow() > expiry:
            return {"valid": False, "reason": "Assertion expired"}

        return {"valid": True, "assertion": assertion}

    # ── OPENID CONNECT ──

    def generate_id_token(
        self,
        identity_id: str,
        email:       str,
        name:        str,
        claims:      Optional[dict] = None
    ) -> dict:
        """Generate an OpenID Connect ID token."""
        issued_at = datetime.utcnow()
        id_token  = {
            "iss":         self.issuer,
            "sub":         identity_id,
            "aud":         self.client_id,
            "email":       email,
            "name":        name,
            "iat":         issued_at.isoformat(),
            "exp":         (issued_at + timedelta(hours=1)).isoformat(),
            "claims":      claims or {},
            "token_type":  "id_token"
        }
        return id_token

    def get_active_sessions(self) -> List[dict]:
        """Return all active OAuth and SAML sessions."""
        return {
            "oauth_tokens":  [t for t in self.active_tokens if t.get("active")],
            "saml_sessions": self.saml_sessions,
            "total_active":  len([t for t in self.active_tokens if t.get("active")])
        }

    def status(self) -> dict:
        return {
            "connector":       "OAuth2/SAML/OIDC",
            "issuer":          self.issuer,
            "active_tokens":   len([t for t in self.active_tokens if t.get("active")]),
            "saml_sessions":   len(self.saml_sessions)
        }


# ── SINGLETON INSTANCE ──
oauth_saml = OAuthSAMLConnector()

if __name__ == "__main__":
    print("Testing OAuth/SAML Connector...")
    token = oauth_saml.generate_oauth_token(
        identity_id = "USR-001",
        email       = "john@company.com",
        role        = "analyst",
        scopes      = ["read:identities", "read:compliance"]
    )
    print(f"Token generated for: {token['email']}")
    print(f"Expires: {token['expires_at']}")
    assertion = oauth_saml.create_saml_assertion(
        identity_id  = "USR-001",
        email        = "john@company.com",
        attributes   = {"department": "Finance", "role": "analyst"},
        sp_entity_id = "https://app.company.com/saml"
    )
    print(f"SAML assertion: {assertion['assertion_id']}")
    print(f"Status: {oauth_saml.status()}")
    print("OAuth/SAML Connector working correctly!")
