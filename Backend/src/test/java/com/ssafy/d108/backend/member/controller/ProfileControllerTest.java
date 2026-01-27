package com.ssafy.d108.backend.member.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.d108.backend.entity.enums.*;
import com.ssafy.d108.backend.member.dto.ProfileResponse;
import com.ssafy.d108.backend.member.dto.ProfileUpdateRequest;
import com.ssafy.d108.backend.member.service.ProfileService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.Set;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = ProfileController.class)
@AutoConfigureMockMvc(addFilters = false) // Disable security filters for simple testing
class ProfileControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProfileService profileService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("내 프로필 수정 테스트 - 성공")
    void updateMyProfile() throws Exception {
        // Given
        Integer userId = 1;

        // Mocking Authentication logic since we disabled filters but Controller expects
        // Authentication
        // Actually since we disabled filters, the Authentication object might be null
        // or we need to inject it via request builder?
        // Wait, ProfileController gets Authentication from arguments.
        // If we duplicate the filter logic or easier: Mock the controller method call
        // directly? No that defeats the purpose.
        // We will pass Principal? No, the controller casts
        // `authentication.getDetails()`.

        // Strategy: Use a custom Authentication object and set it in SecurityContext
        // manually or via `with(authentication(auth))`

        // Mock Request Body
        ProfileUpdateRequest request = new ProfileUpdateRequest();
        request.setHeight(180.5f);
        request.setTopSize(TopSize.L);
        request.setAllergies(Set.of(Allergy.PEANUT));
        request.setEtcAllergy("Peach");

        // Mock Response
        ProfileResponse response = new ProfileResponse();
        response.setUserId(Long.valueOf(userId));
        response.setHeight(180.5f);
        response.setEtcAllergy("Peach");

        given(profileService.updateProfile(eq(userId), any(ProfileUpdateRequest.class))).willReturn(response);

        // Security Context Setup
        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken("customUser", "password");
        auth.setDetails(userId); // Important for ProfileController

        // When & Then
        mockMvc.perform(put("/api/members/profile")
                .principal(auth) // Injects Principal but Controller uses passed Authentication object
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request))
                .with(request1 -> {
                    request1.setUserPrincipal(auth);
                    return request1;
                })
                .with(csrf()))
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.data.etcAllergy").value("Peach"));
    }
}
