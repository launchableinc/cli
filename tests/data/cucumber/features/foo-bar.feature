Feature: foo-bazz
  whenfile name and feature name are defferent
  Scenario: true is true
    Given value is true
    When I ask whether it's true?
    Then I should be told true
