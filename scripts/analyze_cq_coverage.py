#!/usr/bin/env python3
"""
Ontology Competency Question Coverage Analyzer

This script analyzes the waterFRAME ontology to determine which competency
questions can be answered with the current ontology structure, identifies gaps,
and generates updated SPARQL queries that align with the actual ontology concepts.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from enum import Enum


class CoverageLevel(Enum):
    """Coverage level for a competency question"""
    FULL = "Full"  # All concepts present
    PARTIAL = "Partial"  # Some concepts present
    MINIMAL = "Minimal"  # Few concepts present
    NONE = "None"  # No concepts present


@dataclass
class CompetencyQuestion:
    """Represents a competency question with metadata"""
    id: str
    category: str
    text: str
    tag: str  # [O], [O/R], [O/R/M], etc.
    sparql_exists: bool = False
    coverage: CoverageLevel = CoverageLevel.NONE
    present_concepts: List[str] = field(default_factory=list)
    missing_concepts: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class OntologyConcepts:
    """Ontology concepts extracted from TTL files"""
    classes: Set[str] = field(default_factory=set)
    properties: Set[str] = field(default_factory=set)
    object_properties: Set[str] = field(default_factory=set)
    datatype_properties: Set[str] = field(default_factory=set)
    modules: Set[str] = field(default_factory=set)


def parse_competency_questions(filepath: Path) -> Dict[str, CompetencyQuestion]:
    """Parse competency questions from markdown file"""
    questions = {}
    current_category = ""

    with open(filepath, 'r') as f:
        content = f.read()

    # Split into lines
    lines = content.split('\n')

    for line in lines:
        # Detect category headers
        if line.startswith('### '):
            current_category = line.replace('### ', '').strip()
            continue

        # Parse competency question lines
        # Format: - **CQX** [O]: Question text → [SPARQL](path/to/query.rq)
        match = re.match(r'- \*\*(CQ\d+[A-Z]?)\*\* \[([^\]]+)\]: (.+?)(?:→ \[SPARQL\])?', line)
        if match:
            cq_id = match.group(1)
            tag = match.group(2)
            text = match.group(3).strip()

            # Check if SPARQL query exists
            sparql_exists = '→ [SPARQL]' in line

            questions[cq_id] = CompetencyQuestion(
                id=cq_id,
                category=current_category,
                text=text,
                tag=tag,
                sparql_exists=sparql_exists
            )

    return questions


def extract_ontology_concepts(ontology_dir: Path) -> OntologyConcepts:
    """Extract all classes and properties from ontology TTL files"""
    concepts = OntologyConcepts()

    # Find all .ttl files in ontology directory
    ttl_files = list(ontology_dir.rglob('*.ttl'))

    for ttl_file in ttl_files:
        # Track modules
        relative_path = ttl_file.relative_to(ontology_dir)
        module_name = str(relative_path).replace('.ttl', '').replace('/', '_')
        concepts.modules.add(module_name)

        with open(ttl_file, 'r') as f:
            content = f.read()

        # Extract classes (wf:ClassName a owl:Class)
        class_matches = re.findall(r'wf:(\w+)\s+(?:a|rdf:type)\s+owl:Class', content)
        concepts.classes.update(class_matches)

        # Extract object properties
        obj_prop_matches = re.findall(r'wf:(\w+)\s+(?:a|rdf:type)\s+owl:ObjectProperty', content)
        concepts.object_properties.update(obj_prop_matches)
        concepts.properties.update(obj_prop_matches)

        # Extract datatype properties
        data_prop_matches = re.findall(r'wf:(\w+)\s+(?:a|rdf:type)\s+owl:DatatypeProperty', content)
        concepts.datatype_properties.update(data_prop_matches)
        concepts.properties.update(data_prop_matches)

    return concepts


def analyze_cq_coverage(cq: CompetencyQuestion, concepts: OntologyConcepts) -> None:
    """Analyze what concepts are available for a competency question"""

    # Map competency questions to required concepts
    cq_concept_map = {
        'CQ1': {
            'classes': ['WaterSystemComponent', 'WastewaterTreatmentPlant', 'DrinkingWaterPlant',
                       'IndustrialFacility', 'River', 'Catchment'],
            'properties': [],
            'notes': 'Core material entities available'
        },
        'CQ2': {
            'classes': ['WaterSystemComponent', 'Port', 'InputPort', 'OutputPort'],
            'properties': ['flowsTo', 'hasInputPort', 'hasOutputPort'],
            'notes': 'Need flow connection properties - may need to use port-based connections'
        },
        'CQ3': {
            'classes': ['WaterSystemComponent'],
            'properties': ['flowsTo', 'hasInputPort'],
            'notes': 'Input sources via flow/port connections'
        },
        'CQ4': {
            'classes': ['WaterSystemComponent'],
            'properties': ['flowsTo', 'hasOutputPort'],
            'notes': 'Downstream nodes via flow/port connections'
        },
        'CQ5': {
            'classes': ['WaterSystemComponent'],
            'properties': ['flowsTo'],
            'notes': 'Transitive flow path - may need SPARQL property paths'
        },
        'CQ6': {
            'classes': ['WWTPTreatmentProcess', 'PrimaryTreatment', 'SecondaryTreatment', 'TertiaryTreatment'],
            'properties': ['hasSubmodel', 'hasPart'],
            'notes': 'Treatment unit composition'
        },
        'CQ7': {
            'classes': ['WWTPTreatmentProcess'],
            'properties': ['flowsTo', 'hasInputPort', 'hasOutputPort'],
            'notes': 'Treatment train topology via connections'
        },
        'CQ8': {
            'classes': ['WWTPTreatmentProcess', 'WaterQualityParameter'],
            'properties': [],
            'notes': 'Need treatment technology-contaminant mapping'
        },
        'CQ9': {
            'classes': ['WWTPTreatmentProcess', 'TreatmentUnit'],
            'properties': [],
            'notes': 'Need design capacity property'
        },
        'CQ10': {
            'classes': ['WaterQualityParameter', 'WaterQualityObservation', 'BOD', 'COD', 'TSS', 'TotalNitrogen', 'TotalPhosphorus'],
            'properties': ['observedParameter', 'observedValue'],
            'notes': 'Water quality parameters and observations available'
        },
        'CQ11': {
            'classes': ['WaterQualityRequirement', 'RegulatoryStandard', 'LimitType', 'MaximumLimit'],
            'properties': ['hasWaterQualityParameter', 'hasLimitValue', 'hasRegulatoryStandard'],
            'notes': 'Regulatory limits fully supported'
        },
        'CQ12': {
            'classes': ['WaterQualityObservation', 'WaterQualityRequirement', 'ComplianceStatus', 'FitForPurpose'],
            'properties': ['observedParameter', 'hasWaterQualityParameter', 'hasComplianceStatus'],
            'notes': 'Compliance checking supported'
        },
        'CQ13': {
            'classes': ['WaterQualityObservation', 'WaterQualityParameter'],
            'properties': ['observedParameter', 'observedValue'],
            'notes': 'Contaminant detection via observations'
        },
        'CQ14': {
            'classes': [],
            'properties': [],
            'notes': 'Stream classification not yet modeled'
        },
        'CQ15': {
            'classes': ['FitForPurpose', 'IrrigationWater', 'PotableWater', 'IndustrialProcessWater'],
            'properties': [],
            'notes': 'Fit-for-purpose categories available'
        },
        'CQ16': {
            'classes': ['WaterQualityClass', 'WWTPTreatmentProcess'],
            'properties': [],
            'notes': 'Need treatment recommendation logic'
        },
        'CQ17': {
            'classes': ['ProcessModel', 'ComputationalAgent'],
            'properties': ['representsEntity', 'implements', 'simulates'],
            'notes': 'Model-entity mapping available'
        },
        'CQ18': {
            'classes': ['ProcessModel', 'ModelInput', 'ModelVariable', 'InputVariable'],
            'properties': ['hasInput', 'hasInputVariable'],
            'notes': 'Model inputs fully supported'
        },
        'CQ19': {
            'classes': ['ProcessModel', 'ModelOutput', 'ModelVariable', 'OutputVariable'],
            'properties': ['hasOutput', 'hasOutputVariable'],
            'notes': 'Model outputs fully supported'
        },
        'CQ20': {
            'classes': ['ModelVariable', 'DecisionVariable', 'Parameter'],
            'properties': ['isDecisionVariable', 'hasParameter'],
            'notes': 'Decision variables fully supported'
        },
        'CQ21': {
            'classes': ['ModelVariable', 'Parameter'],
            'properties': ['minValue', 'maxValue'],
            'notes': 'Parameter ranges available'
        },
        'CQ22': {
            'classes': ['SoftwareSystem', 'Operation', 'HTTPGrounding'],
            'properties': ['apiEndpoint', 'hasHTTPGrounding', 'httpMethod'],
            'notes': 'API invocation metadata available'
        },
        'CQ23': {
            'classes': ['ModelCapability', 'MassBalance', 'EnergyBalance'],
            'properties': ['hasCapability'],
            'notes': 'Model capabilities fully supported'
        },
        'CQ24': {
            'classes': ['ModelCapability', 'DynamicSimulation', 'SteadyStateSimulation'],
            'properties': ['hasCapability'],
            'notes': 'Time resolution via capability types'
        },
        'CQ25': {
            'classes': ['ComputationalAgent', 'OptimizationAgent'],
            'properties': ['offersOperation'],
            'notes': 'Agent discovery supported'
        },
        'CQ26': {
            'classes': ['OptimizationAgent', 'Operation'],
            'properties': ['hasCapability','offersOperation'],
            'notes': 'Objective function types need extending'
        },
        'CQ27': {
            'classes': ['Operation', 'Precondition', 'Postcondition'],
            'properties': ['hasPrecondition', 'hasPostcondition'],
            'notes': 'Constraint types via conditions'
        },
        'CQ28': {
            'classes': ['OptimizationAgent', 'SoftwareSystem'],
            'properties': ['runsOn'],
            'notes': 'Solver access needs modeling'
        },
        'CQ29': {
            'classes': ['Operation', 'HTTPGrounding'],
            'properties': ['hasHTTPGrounding', 'apiEndpoint'],
            'notes': 'Agent invocation via HTTP grounding'
        },
        'CQ30': {
            'classes': ['DecisionVariable', 'ModelVariable'],
            'properties': ['isDecisionVariable', 'representsEntity'],
            'notes': 'Decision variables by objective'
        },
        'CQ31': {
            'classes': ['Operation', 'ModelInput', 'ModelOutput'],
            'properties': ['producesOutput', 'requiresInput'],
            'notes': 'I/O constraints supported'
        },
        'CQ32': {
            'classes': ['DecisionVariable', 'Catchment'],
            'properties': ['isDecisionVariable'],
            'notes': 'Catchment-wide decision variables'
        },
        'CQ33': {
            'classes': ['ProcessModel', 'Operation'],
            'properties': ['implements', 'offersOperation'],
            'notes': 'Model invocation for solution evaluation'
        },
        'CQ34': {
            'classes': ['ProcessModel', 'WaterQualityObservation'],
            'properties': [],
            'notes': 'Need provenance/timestamp properties'
        },
        'CQ35': {
            'classes': ['RegulatoryStandard'],
            'properties': ['hasRegulatoryStandard'],
            'notes': 'Source of regulatory limits tracked'
        },
        'CQ36': {
            'classes': ['ProcessModel'],
            'properties': [],
            'notes': 'Need maintainer/responsible party'
        },
        'CQ37': {
            'classes': ['ViolationRecord', 'ExceedanceViolation', 'ViolationSeverity'],
            'properties': ['violatingObservation', 'violatedRequirement', 'hasSeverity'],
            'notes': 'Violation tracking fully supported'
        },
        'CQ38': {
            'classes': ['WaterSample', 'SamplingPoint', 'SamplingMethod', 'SamplingEquipment'],
            'properties': ['takenAt', 'usedSamplingMethod', 'collectedBy', 'collectedOn'],
            'notes': 'Chain of custody fully supported'
        },
        'CQ39': {
            'classes': ['LoadCalculation', 'DischargeMeasurement', 'WaterQualityObservation'],
            'properties': ['fromConcentration', 'fromFlowMeasurement', 'calculatedLoad'],
            'notes': 'Load calculation fully supported'
        },
        'CQ40': {
            'classes': ['SamplingPoint', 'InfluentSamplingPoint', 'EffluentSamplingPoint', 'ProcessSamplingPoint', 'AmbientSamplingPoint'],
            'properties': ['locatedAt'],
            'notes': 'Sampling point types fully supported'
        },
    }

    # Get requirements for this CQ
    requirements = cq_concept_map.get(cq.id, {})
    if not requirements:
        cq.coverage = CoverageLevel.NONE
        cq.notes = "Not yet mapped"
        return

    required_classes = set(requirements.get('classes', []))
    required_properties = set(requirements.get('properties', []))
    cq.notes = requirements.get('notes', '')

    # Check what's present
    present_classes = required_classes & concepts.classes
    missing_classes = required_classes - concepts.classes
    present_properties = required_properties & concepts.properties
    missing_properties = required_properties - concepts.properties

    cq.present_concepts = list(present_classes | present_properties)
    cq.missing_concepts = list(missing_classes | missing_properties)

    # Determine coverage level
    if required_classes or required_properties:
        total_required = len(required_classes) + len(required_properties)
        total_present = len(present_classes) + len(present_properties)
        coverage_ratio = total_present / total_required if total_required > 0 else 0

        if coverage_ratio >= 0.9:
            cq.coverage = CoverageLevel.FULL
        elif coverage_ratio >= 0.5:
            cq.coverage = CoverageLevel.PARTIAL
        elif coverage_ratio > 0:
            cq.coverage = CoverageLevel.MINIMAL
        else:
            cq.coverage = CoverageLevel.NONE
    else:
        cq.coverage = CoverageLevel.NONE


def generate_coverage_report(questions: Dict[str, CompetencyQuestion],
                            concepts: OntologyConcepts,
                            output_path: Path) -> None:
    """Generate a detailed coverage report"""

    # Group by category
    categories = {}
    for cq in questions.values():
        if cq.category not in categories:
            categories[cq.category] = []
        categories[cq.category].append(cq)

    # Generate report
    report_lines = [
        "# Competency Question Coverage Analysis",
        "",
        f"**Analysis Date:** {Path(__file__).stat().st_mtime}",
        f"**Ontology Modules:** {len(concepts.modules)}",
        f"**Total Classes:** {len(concepts.classes)}",
        f"**Total Properties:** {len(concepts.properties)}",
        "",
        "## Summary Statistics",
        ""
    ]

    # Calculate statistics
    coverage_counts = {level: 0 for level in CoverageLevel}
    for cq in questions.values():
        coverage_counts[cq.coverage] += 1

    total = len(questions)
    report_lines.extend([
        f"- **Total Competency Questions:** {total}",
        f"- **Full Coverage:** {coverage_counts[CoverageLevel.FULL]} ({coverage_counts[CoverageLevel.FULL]/total*100:.1f}%)",
        f"- **Partial Coverage:** {coverage_counts[CoverageLevel.PARTIAL]} ({coverage_counts[CoverageLevel.PARTIAL]/total*100:.1f}%)",
        f"- **Minimal Coverage:** {coverage_counts[CoverageLevel.MINIMAL]} ({coverage_counts[CoverageLevel.MINIMAL]/total*100:.1f}%)",
        f"- **No Coverage:** {coverage_counts[CoverageLevel.NONE]} ({coverage_counts[CoverageLevel.NONE]/total*100:.1f}%)",
        f"- **Existing SPARQL Queries:** {sum(1 for cq in questions.values() if cq.sparql_exists)}",
        "",
        "## Coverage by Category",
        ""
    ])

    # Detailed coverage by category
    for category, cqs in sorted(categories.items()):
        report_lines.append(f"### {category}")
        report_lines.append("")

        for cq in sorted(cqs, key=lambda x: x.id):
            coverage_icon = {
                CoverageLevel.FULL: "✅",
                CoverageLevel.PARTIAL: "⚠️",
                CoverageLevel.MINIMAL: "⚡",
                CoverageLevel.NONE: "❌"
            }[cq.coverage]

            sparql_icon = "📝" if cq.sparql_exists else "  "

            report_lines.append(f"**{cq.id}** {coverage_icon} {sparql_icon} [{cq.tag}]: {cq.text}")
            report_lines.append(f"- **Coverage:** {cq.coverage.value}")

            if cq.present_concepts:
                report_lines.append(f"- **Present:** {', '.join(sorted(cq.present_concepts))}")
            if cq.missing_concepts:
                report_lines.append(f"- **Missing:** {', '.join(sorted(cq.missing_concepts))}")
            if cq.notes:
                report_lines.append(f"- **Notes:** {cq.notes}")
            report_lines.append("")

    # Write report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"✅ Coverage report written to: {output_path}")


def main():
    """Main analysis function"""
    # Set up paths
    project_root = Path(__file__).parent.parent
    cq_file = project_root / "data" / "competency_questions" / "competency_questions.md"
    ontology_dir = project_root / "data" / "ontology"
    output_dir = project_root / "data" / "competency_questions"

    print("🔍 Analyzing Competency Question Coverage...")
    print(f"   CQ File: {cq_file}")
    print(f"   Ontology Dir: {ontology_dir}")
    print()

    # Parse competency questions
    print("📖 Parsing competency questions...")
    questions = parse_competency_questions(cq_file)
    print(f"   Found {len(questions)} competency questions")

    # Extract ontology concepts
    print("🧬 Extracting ontology concepts...")
    concepts = extract_ontology_concepts(ontology_dir)
    print(f"   Found {len(concepts.classes)} classes")
    print(f"   Found {len(concepts.properties)} properties")
    print(f"   Found {len(concepts.modules)} modules")
    print()

    # Analyze coverage
    print("🔬 Analyzing coverage...")
    for cq_id, cq in questions.items():
        analyze_cq_coverage(cq, concepts)

    # Generate report
    print("📊 Generating coverage report...")
    report_path = output_dir / "coverage_analysis.md"
    generate_coverage_report(questions, concepts, report_path)

    # Print summary
    print()
    print("=" * 60)
    print("COVERAGE SUMMARY")
    print("=" * 60)
    coverage_counts = {level: 0 for level in CoverageLevel}
    for cq in questions.values():
        coverage_counts[cq.coverage] += 1

    for level in CoverageLevel:
        count = coverage_counts[level]
        percentage = count / len(questions) * 100
        print(f"{level.value:12s}: {count:3d} ({percentage:5.1f}%)")

    print("=" * 60)


if __name__ == "__main__":
    main()
