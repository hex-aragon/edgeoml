# Security policy

EdgeOML is research software and is not yet suitable for production security,
payment enforcement, or purchase authorization.

## Reporting

Open a GitHub security advisory for vulnerabilities that could expose private
fingerprint pairs, falsify evidence receipts, bypass nonce or replay checks, or
cause unsafe handling of untrusted model artifacts. Ordinary benchmark bugs
and documentation corrections can use public issues.

Do not include active secret fingerprint material, private model artifacts, API
credentials, personal shopping history, or device attestation secrets in an
issue or pull request.

## Current security boundary

- L0 receipts are self-declared and do not prove that the claimed weights ran.
- L1 device attestation strengthens key and app identity but still trusts the
  app's model measurement.
- L2 measured load and L3 protected execution are research targets, not
  implemented guarantees.
- Published pilot fingerprint pairs are synthetic and must not be reused as
  production ownership secrets.

