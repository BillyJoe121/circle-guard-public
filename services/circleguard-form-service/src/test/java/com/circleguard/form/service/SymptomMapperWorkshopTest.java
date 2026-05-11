package com.circleguard.form.service;

import com.circleguard.form.model.HealthSurvey;
import com.circleguard.form.model.Question;
import com.circleguard.form.model.QuestionType;
import com.circleguard.form.model.Questionnaire;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SymptomMapperWorkshopTest {

    private final SymptomMapper mapper = new SymptomMapper();

    @Test
    void returnsFalseWhenSurveyHasNoDynamicResponses() {
        Questionnaire questionnaire = Questionnaire.builder()
                .questions(List.of(symptomQuestion("Do you have fever?", QuestionType.YES_NO)))
                .build();

        assertFalse(mapper.hasSymptoms(HealthSurvey.builder().build(), questionnaire));
    }

    @Test
    void detectsBreathingDifficultyAsSymptom() {
        Question question = symptomQuestion("Are you having breathing difficulty?", QuestionType.YES_NO);
        Questionnaire questionnaire = Questionnaire.builder().questions(List.of(question)).build();
        HealthSurvey survey = HealthSurvey.builder()
                .responses(Map.of(question.getId().toString(), "YES"))
                .build();

        assertTrue(mapper.hasSymptoms(survey, questionnaire));
    }

    @Test
    void detectsNonEmptySymptomChoiceSelection() {
        Question question = symptomQuestion("Select your symptoms", QuestionType.MULTI_CHOICE);
        Questionnaire questionnaire = Questionnaire.builder().questions(List.of(question)).build();
        HealthSurvey survey = HealthSurvey.builder()
                .responses(Map.of(question.getId().toString(), "[\"headache\"]"))
                .build();

        assertTrue(mapper.hasSymptoms(survey, questionnaire));
    }

    private Question symptomQuestion(String text, QuestionType type) {
        return Question.builder()
                .id(UUID.randomUUID())
                .text(text)
                .type(type)
                .build();
    }
}
