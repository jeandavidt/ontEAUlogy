# Module: compliance

Classes and properties for regulatory compliance checking, violation tracking, and compliance status management. Supports multi-jurisdiction regulatory compliance verification.

**Module URI:** `https://ugentbiomath.github.io/waterframe/modules/compliance`

**Source:** `ontology/modules/compliance.ttl`

**Total Entities:** 52

## Contents

- [Classes](#classes) (27)
- [Object Properties](#object-properties) (11)
- [Datatype Properties](#datatype-properties) (14)

---

## Classes

## AnnualAverageLimit {#https___ugentbiomath.github.io_waterframe_annualaveragelimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#AnnualAverageLimit`

### Labels

- Annual average limit

### Description

Average limit over a calendar year.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## ComplianceCheck {#https___ugentbiomath.github.io_waterframe_compliancecheck}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ComplianceCheck`

### Labels

- Compliance check

### Description

An event where an observation is verified against a regulatory requirement.

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## ComplianceStatus {#https___ugentbiomath.github.io_waterframe_compliancestatus}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ComplianceStatus`

### Labels

- Compliance status

### Description

The compliance status of an observation or measurement with respect to regulatory requirements.

### Subclasses

- [Compliant](#https___ugentbiomath.github.io_waterframe_compliant)
- [NonCompliant](#https___ugentbiomath.github.io_waterframe_noncompliant)
- [NotApplicable](#https___ugentbiomath.github.io_waterframe_notapplicable)
- [PendingReview](#https___ugentbiomath.github.io_waterframe_pendingreview)

### Related Entities

- [Compliant](#https___ugentbiomath.github.io_waterframe_compliant)
- [NonCompliant](#https___ugentbiomath.github.io_waterframe_noncompliant)
- [NotApplicable](#https___ugentbiomath.github.io_waterframe_notapplicable)
- [PendingReview](#https___ugentbiomath.github.io_waterframe_pendingreview)


---

## Compliant {#https___ugentbiomath.github.io_waterframe_compliant}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#Compliant`

### Labels

- Compliant

### Description

Observation meets all applicable regulatory requirements.

### Superclasses

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)

### Related Entities

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)


---

## ConcentrationLimit {#https___ugentbiomath.github.io_waterframe_concentrationlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ConcentrationLimit`

### Labels

- Concentration limit

### Description

Limit expressed as concentration (e.g., mg/L, ug/L).

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## CriticalViolation {#https___ugentbiomath.github.io_waterframe_criticalviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#CriticalViolation`

### Labels

- Critical violation

### Description

Critical violation requiring immediate response.

### Superclasses

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)

### Related Entities

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)


---

## DailyMaximumLimit {#https___ugentbiomath.github.io_waterframe_dailymaximumlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DailyMaximumLimit`

### Labels

- Daily maximum limit

### Description

Maximum value allowed in any single day.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## DeficiencyViolation {#https___ugentbiomath.github.io_waterframe_deficiencyviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#DeficiencyViolation`

### Labels

- Deficiency violation

### Description

Violation where measured value falls below minimum limit.

### Superclasses

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## ExceedanceViolation {#https___ugentbiomath.github.io_waterframe_exceedanceviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ExceedanceViolation`

### Labels

- Exceedance violation

### Description

Violation where measured value exceeds maximum limit.

### Superclasses

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## LoadCalculation {#https___ugentbiomath.github.io_waterframe_loadcalculation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#LoadCalculation`

### Labels

- Load calculation

### Description

Derivation of pollutant load from concentration observation and flow measurement. Load = Concentration x Flow x conversion factor.

### Superclasses

- [BFO_0000015](#https___ugentbiomath.github.io_waterframe_bfo_0000015)


---

## LoadLimit {#https___ugentbiomath.github.io_waterframe_loadlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#LoadLimit`

### Labels

- Load limit

### Description

Limit expressed as mass per unit time (e.g., kg/day, lbs/day). Calculated as concentration x flow.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## MinorViolation {#https___ugentbiomath.github.io_waterframe_minorviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MinorViolation`

### Labels

- Minor violation

### Description

Minor technical violation, typically addressed through notification.

### Superclasses

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)

### Related Entities

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)


---

## ModerateViolation {#https___ugentbiomath.github.io_waterframe_moderateviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ModerateViolation`

### Labels

- Moderate violation

### Description

Significant violation requiring corrective action.

### Superclasses

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)

### Related Entities

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)


---

## MonthlyAverageLimit {#https___ugentbiomath.github.io_waterframe_monthlyaveragelimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#MonthlyAverageLimit`

### Labels

- Monthly average limit

### Description

Average limit over a calendar month.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## NonCompliant {#https___ugentbiomath.github.io_waterframe_noncompliant}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#NonCompliant`

### Labels

- Non-compliant

### Description

Observation exceeds one or more regulatory limits.

### Superclasses

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)

### Related Entities

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)


---

## NotApplicable {#https___ugentbiomath.github.io_waterframe_notapplicable}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#NotApplicable`

### Labels

- Not applicable

### Description

No applicable regulatory requirement exists for this observation.

### Superclasses

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)

### Related Entities

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)


---

## PendingReview {#https___ugentbiomath.github.io_waterframe_pendingreview}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PendingReview`

### Labels

- Pending review

### Description

Compliance status not yet determined or under review.

### Superclasses

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)

### Related Entities

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)


---

## PercentRemovalLimit {#https___ugentbiomath.github.io_waterframe_percentremovallimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#PercentRemovalLimit`

### Labels

- Percent removal limit

### Description

Limit expressed as minimum removal efficiency (e.g., 85% BOD removal).

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## RangeViolation {#https___ugentbiomath.github.io_waterframe_rangeviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#RangeViolation`

### Labels

- Range violation

### Description

Violation where measured value falls outside allowed range.

### Superclasses

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## ReportingViolation {#https___ugentbiomath.github.io_waterframe_reportingviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ReportingViolation`

### Labels

- Reporting violation

### Description

Violation of reporting requirements (deadline, format, etc.).

### Superclasses

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## SamplingViolation {#https___ugentbiomath.github.io_waterframe_samplingviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SamplingViolation`

### Labels

- Sampling violation

### Description

Violation of sampling requirements (frequency, method, etc.).

### Superclasses

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## SeriousViolation {#https___ugentbiomath.github.io_waterframe_seriousviolation}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#SeriousViolation`

### Labels

- Serious violation

### Description

Serious violation with potential environmental or health impact.

### Superclasses

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)

### Related Entities

- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)


---

## TechnologyBasedLimit {#https___ugentbiomath.github.io_waterframe_technologybasedlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#TechnologyBasedLimit`

### Labels

- Technology-based effluent limit (TBEL)

### Description

Minimum level of effluent quality attainable by available technology. Common in USEPA permits.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## ViolationRecord {#https___ugentbiomath.github.io_waterframe_violationrecord}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ViolationRecord`

### Labels

- Violation record

### Description

A record documenting a regulatory violation.

### Superclasses

- [BFO_0000031](#https___ugentbiomath.github.io_waterframe_bfo_0000031)

### Subclasses

- [DeficiencyViolation](#https___ugentbiomath.github.io_waterframe_deficiencyviolation)
- [ExceedanceViolation](#https___ugentbiomath.github.io_waterframe_exceedanceviolation)
- [RangeViolation](#https___ugentbiomath.github.io_waterframe_rangeviolation)
- [ReportingViolation](#https___ugentbiomath.github.io_waterframe_reportingviolation)
- [SamplingViolation](#https___ugentbiomath.github.io_waterframe_samplingviolation)

### Related Entities

- [DeficiencyViolation](#https___ugentbiomath.github.io_waterframe_deficiencyviolation)
- [ExceedanceViolation](#https___ugentbiomath.github.io_waterframe_exceedanceviolation)
- [RangeViolation](#https___ugentbiomath.github.io_waterframe_rangeviolation)
- [ReportingViolation](#https___ugentbiomath.github.io_waterframe_reportingviolation)
- [SamplingViolation](#https___ugentbiomath.github.io_waterframe_samplingviolation)


---

## ViolationSeverity {#https___ugentbiomath.github.io_waterframe_violationseverity}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#ViolationSeverity`

### Labels

- Violation severity

### Description

Classification of violation severity for prioritization and response.

### Subclasses

- [CriticalViolation](#https___ugentbiomath.github.io_waterframe_criticalviolation)
- [MinorViolation](#https___ugentbiomath.github.io_waterframe_minorviolation)
- [ModerateViolation](#https___ugentbiomath.github.io_waterframe_moderateviolation)
- [SeriousViolation](#https___ugentbiomath.github.io_waterframe_seriousviolation)

### Related Entities

- [CriticalViolation](#https___ugentbiomath.github.io_waterframe_criticalviolation)
- [MinorViolation](#https___ugentbiomath.github.io_waterframe_minorviolation)
- [ModerateViolation](#https___ugentbiomath.github.io_waterframe_moderateviolation)
- [SeriousViolation](#https___ugentbiomath.github.io_waterframe_seriousviolation)


---

## WaterQualityBasedLimit {#https___ugentbiomath.github.io_waterframe_waterqualitybasedlimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WaterQualityBasedLimit`

### Labels

- Water quality-based effluent limit (WQBEL)

### Description

Limit required to protect receiving water quality standards. More stringent than technology-based.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## WeeklyAverageLimit {#https___ugentbiomath.github.io_waterframe_weeklyaveragelimit}

**Type:** Class

**URI:** `https://ugentbiomath.github.io/waterframe#WeeklyAverageLimit`

### Labels

- Weekly average limit

### Description

Average limit over a 7-day period.

### Superclasses

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)

### Related Entities

- [LimitType](#https___ugentbiomath.github.io_waterframe_limittype)


---

## Object Properties

## againstRequirement {#https___ugentbiomath.github.io_waterframe_againstrequirement}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#againstRequirement`

### Labels

- against requirement

### Description

Links a compliance check to the requirement being checked against

### Domains

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)

### Ranges

- WaterQualityRequirement

### Related Entities

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)
- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## checksObservation {#https___ugentbiomath.github.io_waterframe_checksobservation}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#checksObservation`

### Labels

- checks observation

### Description

Links a compliance check to the observation being verified

### Domains

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)

### Ranges

- WaterQualityObservation

### Related Entities

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)
- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## fromConcentration {#https___ugentbiomath.github.io_waterframe_fromconcentration}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#fromConcentration`

### Labels

- from concentration

### Description

Links a load calculation to its source concentration observation

### Domains

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)

### Ranges

- WaterQualityObservation

### Related Entities

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)
- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## fromFlowMeasurement {#https___ugentbiomath.github.io_waterframe_fromflowmeasurement}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#fromFlowMeasurement`

### Labels

- from flow measurement

### Description

Links a load calculation to its source flow measurement

### Domains

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)

### Ranges

- DischargeMeasurement

### Related Entities

- [DischargeMeasurement](#https___ugentbiomath.github.io_waterframe_dischargemeasurement)
- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)


---

## generatesViolation {#https___ugentbiomath.github.io_waterframe_generatesviolation}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#generatesViolation`

### Labels

- generates violation

### Description

Links a compliance check to a violation record if non-compliant

### Domains

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)

### Ranges

- ViolationRecord

### Related Entities

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)
- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## hasComplianceStatus {#https___ugentbiomath.github.io_waterframe_hascompliancestatus}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasComplianceStatus`

### Labels

- has compliance status

### Description

Links an observation to its compliance status

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- ComplianceStatus

### Related Entities

- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)
- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## hasSeverity {#https___ugentbiomath.github.io_waterframe_hasseverity}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasSeverity`

### Labels

- has severity

### Description

Links a violation to its severity classification

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- ViolationSeverity

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)
- [ViolationSeverity](#https___ugentbiomath.github.io_waterframe_violationseverity)


---

## loadUnit {#https___ugentbiomath.github.io_waterframe_loadunit}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#loadUnit`

### Labels

- load unit

### Description

Unit of the calculated load (e.g., kg/day)

### Domains

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)

### Ranges

- Unit

### Related Entities

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)


---

## resultsIn {#https___ugentbiomath.github.io_waterframe_resultsin}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#resultsIn`

### Labels

- results in

### Description

Links a compliance check to its resulting status

### Domains

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)

### Ranges

- ComplianceStatus

### Related Entities

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)
- [ComplianceStatus](#https___ugentbiomath.github.io_waterframe_compliancestatus)


---

## violatedRequirement {#https___ugentbiomath.github.io_waterframe_violatedrequirement}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#violatedRequirement`

### Labels

- violated requirement

### Description

Links a violation to the requirement that was violated

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- WaterQualityRequirement

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)
- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## violatingObservation {#https___ugentbiomath.github.io_waterframe_violatingobservation}

**Type:** Object Property

**URI:** `https://ugentbiomath.github.io/waterframe#violatingObservation`

### Labels

- violating observation

### Description

Links a violation to the observation that caused it

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- WaterQualityObservation

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)
- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## Datatype Properties

## calculatedLoad {#https___ugentbiomath.github.io_waterframe_calculatedload}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#calculatedLoad`

### Labels

- calculated load

### Description

The calculated pollutant load value

### Domains

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)

### Ranges

- double

### Related Entities

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)


---

## calculatedOn {#https___ugentbiomath.github.io_waterframe_calculatedon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#calculatedOn`

### Labels

- calculated on

### Description

Date and time when load was calculated

### Domains

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)

### Ranges

- dateTime

### Related Entities

- [LoadCalculation](#https___ugentbiomath.github.io_waterframe_loadcalculation)


---

## checkedOn {#https___ugentbiomath.github.io_waterframe_checkedon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#checkedOn`

### Labels

- checked on

### Description

Date and time when compliance was verified

### Domains

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)

### Ranges

- dateTime

### Related Entities

- [ComplianceCheck](#https___ugentbiomath.github.io_waterframe_compliancecheck)


---

## effectiveFrom {#https___ugentbiomath.github.io_waterframe_effectivefrom}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#effectiveFrom`

### Labels

- effective from

### Description

Date from which the requirement is effective

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- date

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## effectiveUntil {#https___ugentbiomath.github.io_waterframe_effectiveuntil}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#effectiveUntil`

### Labels

- effective until

### Description

Date until which the requirement is effective

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- date

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasAveragingPeriod {#https___ugentbiomath.github.io_waterframe_hasaveragingperiod}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasAveragingPeriod`

### Labels

- has averaging period

### Description

Averaging period for the limit (e.g., 30 days, 7 days)

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- string

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasLowerLimitValue {#https___ugentbiomath.github.io_waterframe_haslowerlimitvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasLowerLimitValue`

### Labels

- has lower limit value

### Description

The lower bound of a range limit

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- double

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasMinRemovalPercent {#https___ugentbiomath.github.io_waterframe_hasminremovalpercent}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasMinRemovalPercent`

### Labels

- has minimum removal percent

### Description

Minimum percent removal required

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- double

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## hasUpperLimitValue {#https___ugentbiomath.github.io_waterframe_hasupperlimitvalue}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#hasUpperLimitValue`

### Labels

- has upper limit value

### Description

The upper bound of a range limit

### Domains

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)

### Ranges

- double

### Related Entities

- [WaterQualityRequirement](#https___ugentbiomath.github.io_waterframe_waterqualityrequirement)


---

## lastCheckedOn {#https___ugentbiomath.github.io_waterframe_lastcheckedon}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#lastCheckedOn`

### Labels

- last checked on

### Description

Date and time of most recent compliance check

### Domains

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)

### Ranges

- dateTime

### Related Entities

- [WaterQualityObservation](#https___ugentbiomath.github.io_waterframe_waterqualityobservation)


---

## violationAmount {#https___ugentbiomath.github.io_waterframe_violationamount}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#violationAmount`

### Labels

- violation amount

### Description

The amount by which the limit was exceeded (positive) or deficient (negative)

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- double

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## violationDate {#https___ugentbiomath.github.io_waterframe_violationdate}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#violationDate`

### Labels

- violation date

### Description

Date when the violation occurred

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- date

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## violationId {#https___ugentbiomath.github.io_waterframe_violationid}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#violationId`

### Labels

- violation ID

### Description

Unique identifier for regulatory tracking of the violation

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- string

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

## violationPercentage {#https___ugentbiomath.github.io_waterframe_violationpercentage}

**Type:** Datatype Property

**URI:** `https://ugentbiomath.github.io/waterframe#violationPercentage`

### Labels

- violation percentage

### Description

Percentage by which the limit was exceeded ((observed - limit) / limit * 100)

### Domains

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)

### Ranges

- double

### Related Entities

- [ViolationRecord](#https___ugentbiomath.github.io_waterframe_violationrecord)


---

