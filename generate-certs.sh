#!/bin/bash
# Generate self-signed SSL certificates for development/testing
# For production, use Let's Encrypt or a trusted CA

set -e

CERT_DIR="./certs"
DOMAIN="titouservice.ltjs.net"

mkdir -p "$CERT_DIR"

if [ -f "$CERT_DIR/cert.pem" ] && [ -f "$CERT_DIR/key.pem" ]; then
    echo "Certificates already exist in $CERT_DIR"
    exit 0
fi

echo "Generating self-signed certificate for $DOMAIN..."

openssl req -x509 -newkey rsa:2048 -nodes \
    -out "$CERT_DIR/cert.pem" \
    -keyout "$CERT_DIR/key.pem" \
    -days 365 \
    -subj "/CN=$DOMAIN"

echo "✓ Certificates generated in $CERT_DIR"
echo "  - Certificate: $CERT_DIR/cert.pem"
echo "  - Private key: $CERT_DIR/key.pem"
echo ""
echo "⚠️  WARNING: These are self-signed certificates for development only!"
echo "For production, use Let's Encrypt or a trusted Certificate Authority."
