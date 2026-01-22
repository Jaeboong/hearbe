package project2.pro.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ProController {

    @GetMapping("/hello")
    public String index(Model model) {
        model.addAttribute("message", "시각장애인을 위한 AI 쇼핑 에이전트 서비스입니다.");
        return "index";
    }

    // 시각장애인 사용자용 페이지
    @GetMapping("/user")
    public String userPage(Model model) {
        model.addAttribute("role", "USER");
        return "user-view"; // user-view.html 파일
    }

    // 보호자용 페이지
    @GetMapping("/guardian")
    public String guardianPage(Model model) {
        model.addAttribute("role", "GUARDIAN");
        return "guardian-view"; // guardian-view.html 파일
    }
}
