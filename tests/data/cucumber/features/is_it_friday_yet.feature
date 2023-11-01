Feature: Is it Friday yet?
  Everybody wants to know when it's Friday

  Background:
    Given this year is 2023
    And this month is January

  Scenario Outline: Today is or is not Friday
    Given today is "<day>"
    When I ask whether it's Friday yet
    Then I should be told "<answer>"

    Examples:
      | day            | answer |
      | Friday         | TGIF   |
      | Sunday         | Nope   |
      | anything else! | Nope   |

  Scenario: Sunday isn't Friday
    Given today is Sunday
    Given it is sunny today
    Given the current UTC is 01:00 AM
    Given the current EST is 08:00 PM
    Given the current JST is 10:00 AM
    When I ask whether it's Friday yet
    Then I should be told "Nope"

  Scenario: Friday is Friday
    Given today is Friday
    When I ask whether it's Friday yet
    Then I should be told "TGIF"

  Scenario: This is fail
    Given today is Friday
    When I ask whether it's Friday yet
    Then I should be told "Nope"
