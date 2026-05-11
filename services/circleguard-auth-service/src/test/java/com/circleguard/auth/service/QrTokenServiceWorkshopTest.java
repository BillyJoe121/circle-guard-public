package com.circleguard.auth.service;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class QrTokenServiceWorkshopTest {

    private static final String SECRET = "my-qr-secret-key-for-dev-1234567890";

    @Test
    void generatedQrTokenUsesAnonymousIdAsSubject() {
        UUID anonymousId = UUID.randomUUID();
        QrTokenService service = new QrTokenService(SECRET, 60_000);

        Claims claims = parse(service.generateQrToken(anonymousId));

        assertEquals(anonymousId.toString(), claims.getSubject());
    }

    @Test
    void generatedQrTokenHonorsConfiguredExpirationWindow() {
        UUID anonymousId = UUID.randomUUID();
        QrTokenService service = new QrTokenService(SECRET, 120_000);

        Claims claims = parse(service.generateQrToken(anonymousId));
        long lifetimeMillis = claims.getExpiration().getTime() - claims.getIssuedAt().getTime();

        assertTrue(lifetimeMillis >= 119_000 && lifetimeMillis <= 121_000);
    }

    private Claims parse(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(Keys.hmacShaKeyFor(SECRET.getBytes()))
                .build()
                .parseClaimsJws(token)
                .getBody();
    }
}
