package project2.pro.configuration;
import project2.pro.configuration.SignalHandler;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocket
public class WebSocketConfiguration implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // "/signal" 엔드포인트로 웹소켓 핸들러 등록
        registry.addHandler(new SignalHandler(), "/signal")
                .setAllowedOrigins("*"); // 실제 서비스 시 도메인 제한 필요
    }
}