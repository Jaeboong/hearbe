package com.ssafy.d108.backend.member.dto;

import com.ssafy.d108.backend.entity.Profile;
import com.ssafy.d108.backend.entity.User;
import com.ssafy.d108.backend.entity.enums.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;
import java.util.Set;

@Getter
@Setter
@NoArgsConstructor
public class ProfileResponse {

    private Long userId;
    private String username;
    private String email;
    private UserType userType;
    private String phoneNumber;

    // Profile Info
    private Gender gender;
    private LocalDate birthDate;
    private Float height;
    private Float weight;

    // Sizes
    private TopSize topSize;
    private BottomSize bottomSize;
    private ShoeSize shoeSize;

    // Allergies
    private Set<Allergy> allergies;
    private String etcAllergy;

    public static ProfileResponse rom(User user, Profile profile) {
        ProfileResponse response = new ProfileResponse();
        response.setUserId(Long.valueOf(user.getId()));
        response.setUsername(user.getName());
        response.setEmail(user.getEmail());
        response.setUserType(user.getUserType());
        response.setPhoneNumber(user.getPhoneNumber());

        if (profile != null) {
            response.setGender(profile.getGender());
            response.setBirthDate(profile.getBirthDate());
            response.setHeight(profile.getHeight());
            response.setWeight(profile.getWeight());
            response.setTopSize(profile.getTopSize());
            response.setBottomSize(profile.getBottomSize());
            response.setShoeSize(profile.getShoeSize());
            response.setAllergies(profile.getAllergies());
            response.setEtcAllergy(profile.getEtcAllergy());
        }
        return response;
    }

    // Constructor for convenience if needed
    public static ProfileResponse of(User user, Profile profile) {
        return rom(user, profile);
    }
}
