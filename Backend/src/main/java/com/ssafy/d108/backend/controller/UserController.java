package com.ssafy.d108.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/users")
public class UserController {

    /**
     * 사용자 본인 정보 조회 (임시)
     */
    @GetMapping("/me")
    public String getMyInfo() {
        return "user info";
    }
}