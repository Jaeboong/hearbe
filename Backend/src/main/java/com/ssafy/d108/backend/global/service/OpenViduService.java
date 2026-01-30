package com.ssafy.d108.backend.global.service;

import io.openvidu.java.client.*;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class OpenViduService {

    @Value("${OPENVIDU_URL}")
    private String openviduUrl;

    @Value("${OPENVIDU_SECRET}")
    private String openviduSecret;

    private OpenVidu openvidu;

    @PostConstruct
    public void init() {
        // Disable SSL Verification for Localhost Development
        try {
            javax.net.ssl.TrustManager[] trustAllCerts = new javax.net.ssl.TrustManager[] {
                    new javax.net.ssl.X509TrustManager() {
                        public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                            return null;
                        }

                        public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                        }

                        public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                        }
                    }
            };
            javax.net.ssl.SSLContext sc = javax.net.ssl.SSLContext.getInstance("SSL");
            sc.init(null, trustAllCerts, new java.security.SecureRandom());

            // Apply globally
            javax.net.ssl.HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
            javax.net.ssl.HttpsURLConnection.setDefaultHostnameVerifier((hostname, session) -> true);
            javax.net.ssl.SSLContext.setDefault(sc);
        } catch (Exception e) {
            log.warn("Failed to disable SSL verification", e);
        }

        this.openvidu = new OpenVidu(openviduUrl, openviduSecret);
        log.info("Initialized OpenVidu client with URL: {}", openviduUrl);
    }

    public Session createSession() throws OpenViduJavaClientException, OpenViduHttpException {
        SessionProperties properties = new SessionProperties.Builder().build();
        return this.openvidu.createSession(properties);
    }

    public String createConnection(String sessionId, OpenViduRole role)
            throws OpenViduJavaClientException, OpenViduHttpException {
        Session session = this.openvidu.getActiveSession(sessionId);
        if (session == null) {
            // If the session is not valid, try to fetch it or handle error
            // Check if it exists for OpenVidu Server, but not locally
            // In a real production scenario, we might need to fetch active sessions
            return null;
        }

        ConnectionProperties properties = new ConnectionProperties.Builder()
                .type(ConnectionType.WEBRTC)
                .role(role)
                .build();
        return session.createConnection(properties).getToken();
    }
}
