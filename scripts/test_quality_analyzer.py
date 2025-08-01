#!/usr/bin/env python3
"""
Test Quality Analyzer for the Legal Document Summarizer.
Analyzes test coverage, quality metrics, and generates improvement recommendations.
"""

import os
import sys
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse


class TestQualityAnalyzer:
    """Analyzes test quality and provides improvement recommendations."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.coverage_data = {}
        self.test_results = {}
        self.quality_metrics = {
            'coverage_percentage': 0.0,
            'test_count': 0,
            'test_success_rate': 0.0,
            'critical_coverage': 0.0,
            'code_complexity': 0.0,
            'test_maintainability': 0.0
        }
        
        # Quality thresholds
        self.thresholds = {
            'min_coverage': 85.0,
            'critical_coverage': 95.0,
            'min_success_rate': 95.0,
            'max_complexity': 10.0,
            'min_maintainability': 7.0
        }
        
        # Critical components that need high coverage
        self.critical_components = [
            'src/services/summarizer.py',
            'src/services/document_handler.py',
            'src/services/text_extractor.py',
            'src/utils/error_handler.py',
            'src/services/security_service.py'
        ]

    def analyze_test_quality(self) -> Dict:
        """Perform comprehensive test quality analysis."""
        print("🔍 Analyzing Test Quality")
        print("=" * 50)
        
        # Analyze coverage
        coverage_analysis = self._analyze_coverage()
        
        # Analyze test results
        test_analysis = self._analyze_test_results()
        
        # Analyze code complexity
        complexity_analysis = self._analyze_code_complexity()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            coverage_analysis, test_analysis, complexity_analysis
        )
        
        # Compile final report
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'coverage_analysis': coverage_analysis,
            'test_analysis': test_analysis,
            'complexity_analysis': complexity_analysis,
            'recommendations': recommendations,
            'quality_score': self._calculate_quality_score(),
            'thresholds_met': self._check_thresholds()
        }
        
        # Generate reports
        self._generate_quality_report(quality_report)
        
        return quality_report

    def _analyze_coverage(self) -> Dict:
        """Analyze test coverage data."""
        print("📊 Analyzing Coverage Data...")
        
        coverage_file = Path('coverage.xml')
        if not coverage_file.exists():
            print("⚠️  No coverage.xml found. Running coverage analysis...")
            self._generate_coverage_report()
        
        if coverage_file.exists():
            coverage_data = self._parse_coverage_xml('coverage.xml')
        else:
            print("❌ Could not generate coverage data")
            coverage_data = {'overall': 0.0, 'by_file': {}, 'critical': 0.0}
        
        # Analyze critical component coverage
        critical_coverage = self._analyze_critical_coverage(coverage_data)
        
        analysis = {
            'overall_coverage': coverage_data.get('overall', 0.0),
            'file_coverage': coverage_data.get('by_file', {}),
            'critical_coverage': critical_coverage,
            'coverage_gaps': self._identify_coverage_gaps(coverage_data),
            'low_coverage_files': self._find_low_coverage_files(coverage_data)
        }
        
        self.quality_metrics['coverage_percentage'] = analysis['overall_coverage']
        self.quality_metrics['critical_coverage'] = critical_coverage
        
        return analysis

    def _analyze_test_results(self) -> Dict:
        """Analyze test execution results."""
        print("🧪 Analyzing Test Results...")
        
        test_files = list(Path('.').glob('test_results_*.json'))
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        test_durations = []
        
        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    data = json.load(f)
                    
                if 'summary' in data:
                    total_tests += data['summary'].get('total', 0)
                    passed_tests += data['summary'].get('passed', 0)
                    failed_tests += data['summary'].get('failed', 0)
                    skipped_tests += data['summary'].get('skipped', 0)
                    
                if 'duration' in data:
                    test_durations.append(data['duration'])
                    
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_duration = sum(test_durations) / len(test_durations) if test_durations else 0
        
        analysis = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'success_rate': success_rate,
            'average_duration': avg_duration,
            'test_distribution': self._analyze_test_distribution()
        }
        
        self.quality_metrics['test_count'] = total_tests
        self.quality_metrics['test_success_rate'] = success_rate
        
        return analysis

    def _analyze_code_complexity(self) -> Dict:
        """Analyze code complexity metrics."""
        print("🔧 Analyzing Code Complexity...")
        
        try:
            # Use radon to analyze complexity
            result = subprocess.run(
                ['python', '-m', 'radon', 'cc', 'src/', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                complexity_analysis = self._process_complexity_data(complexity_data)
            else:
                complexity_analysis = {'average_complexity': 0, 'high_complexity_files': []}
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            complexity_analysis = {'average_complexity': 0, 'high_complexity_files': []}
        
        self.quality_metrics['code_complexity'] = complexity_analysis.get('average_complexity', 0)
        
        return complexity_analysis

    def _generate_coverage_report(self):
        """Generate coverage report."""
        try:
            subprocess.run([
                'python', '-m', 'pytest', 'tests/unit/', 
                '--cov=src', '--cov-report=xml', '--cov-report=html'
            ], timeout=300, check=True)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            print("⚠️  Could not generate coverage report")

    def _parse_coverage_xml(self, filename: str) -> Dict:
        """Parse coverage XML file."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            
            # Get overall coverage
            overall_coverage = float(root.attrib.get('line-rate', 0)) * 100
            
            # Get file-level coverage
            file_coverage = {}
            for package in root.findall('.//package'):
                for class_elem in package.findall('.//class'):
                    filename = class_elem.attrib.get('filename', '')
                    line_rate = float(class_elem.attrib.get('line-rate', 0)) * 100
                    file_coverage[filename] = line_rate
            
            return {
                'overall': overall_coverage,
                'by_file': file_coverage
            }
            
        except (ET.ParseError, FileNotFoundError, ValueError):
            return {'overall': 0.0, 'by_file': {}}

    def _analyze_critical_coverage(self, coverage_data: Dict) -> float:
        """Analyze coverage of critical components."""
        critical_files = []
        file_coverage = coverage_data.get('by_file', {})
        
        for critical_file in self.critical_components:
            # Find matching files (handle path variations)
            matching_files = [f for f in file_coverage.keys() if critical_file.replace('/', os.sep) in f]
            if matching_files:
                critical_files.extend([file_coverage[f] for f in matching_files])
        
        return sum(critical_files) / len(critical_files) if critical_files else 0.0

    def _identify_coverage_gaps(self, coverage_data: Dict) -> List[str]:
        """Identify files with coverage gaps."""
        gaps = []
        file_coverage = coverage_data.get('by_file', {})
        
        for filename, coverage in file_coverage.items():
            if coverage < self.thresholds['min_coverage']:
                gaps.append(f"{filename}: {coverage:.1f}%")
        
        return gaps

    def _find_low_coverage_files(self, coverage_data: Dict) -> List[Dict]:
        """Find files with low coverage."""
        low_coverage = []
        file_coverage = coverage_data.get('by_file', {})
        
        for filename, coverage in file_coverage.items():
            if coverage < self.thresholds['min_coverage']:
                low_coverage.append({
                    'file': filename,
                    'coverage': coverage,
                    'gap': self.thresholds['min_coverage'] - coverage
                })
        
        return sorted(low_coverage, key=lambda x: x['gap'], reverse=True)

    def _analyze_test_distribution(self) -> Dict:
        """Analyze distribution of tests across categories."""
        test_dirs = ['unit', 'integration', 'performance', 'edge_cases', 'security']
        distribution = {}
        
        for test_dir in test_dirs:
            test_path = Path(f'tests/{test_dir}')
            if test_path.exists():
                test_files = list(test_path.glob('test_*.py'))
                distribution[test_dir] = len(test_files)
            else:
                distribution[test_dir] = 0
        
        return distribution

    def _process_complexity_data(self, complexity_data: Dict) -> Dict:
        """Process complexity data from radon."""
        all_complexities = []
        high_complexity_files = []
        
        for filename, functions in complexity_data.items():
            for func_data in functions:
                complexity = func_data.get('complexity', 0)
                all_complexities.append(complexity)
                
                if complexity > self.thresholds['max_complexity']:
                    high_complexity_files.append({
                        'file': filename,
                        'function': func_data.get('name', 'unknown'),
                        'complexity': complexity
                    })
        
        avg_complexity = sum(all_complexities) / len(all_complexities) if all_complexities else 0
        
        return {
            'average_complexity': avg_complexity,
            'high_complexity_files': high_complexity_files,
            'complexity_distribution': self._calculate_complexity_distribution(all_complexities)
        }

    def _calculate_complexity_distribution(self, complexities: List[int]) -> Dict:
        """Calculate complexity distribution."""
        if not complexities:
            return {'low': 0, 'medium': 0, 'high': 0}
        
        low = sum(1 for c in complexities if c <= 5)
        medium = sum(1 for c in complexities if 5 < c <= 10)
        high = sum(1 for c in complexities if c > 10)
        
        total = len(complexities)
        
        return {
            'low': (low / total) * 100,
            'medium': (medium / total) * 100,
            'high': (high / total) * 100
        }

    def _generate_recommendations(self, coverage_analysis: Dict, 
                                test_analysis: Dict, complexity_analysis: Dict) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Coverage recommendations
        if coverage_analysis['overall_coverage'] < self.thresholds['min_coverage']:
            recommendations.append(
                f"📈 Increase overall test coverage from {coverage_analysis['overall_coverage']:.1f}% "
                f"to at least {self.thresholds['min_coverage']}%"
            )
        
        if coverage_analysis['critical_coverage'] < self.thresholds['critical_coverage']:
            recommendations.append(
                f"🎯 Improve critical component coverage from {coverage_analysis['critical_coverage']:.1f}% "
                f"to at least {self.thresholds['critical_coverage']}%"
            )
        
        # Add specific file recommendations
        for file_info in coverage_analysis['low_coverage_files'][:3]:  # Top 3
            recommendations.append(
                f"📄 Add tests for {file_info['file']} (current: {file_info['coverage']:.1f}%)"
            )
        
        # Test success rate recommendations
        if test_analysis['success_rate'] < self.thresholds['min_success_rate']:
            recommendations.append(
                f"🔧 Fix failing tests to improve success rate from {test_analysis['success_rate']:.1f}% "
                f"to at least {self.thresholds['min_success_rate']}%"
            )
        
        # Complexity recommendations
        if complexity_analysis.get('high_complexity_files'):
            recommendations.append(
                f"🔨 Refactor {len(complexity_analysis['high_complexity_files'])} high-complexity functions"
            )
        
        # Test distribution recommendations
        distribution = test_analysis.get('test_distribution', {})
        if distribution.get('edge_cases', 0) < 2:
            recommendations.append("🧪 Add more edge case tests for better robustness")
        
        if distribution.get('security', 0) < 1:
            recommendations.append("🔒 Add security-focused tests")
        
        return recommendations

    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)."""
        weights = {
            'coverage': 0.3,
            'success_rate': 0.25,
            'critical_coverage': 0.25,
            'complexity': 0.2
        }
        
        # Normalize metrics to 0-100 scale
        coverage_score = min(self.quality_metrics['coverage_percentage'], 100)
        success_score = min(self.quality_metrics['test_success_rate'], 100)
        critical_score = min(self.quality_metrics['critical_coverage'], 100)
        
        # Complexity score (inverse - lower complexity is better)
        complexity_score = max(0, 100 - (self.quality_metrics['code_complexity'] * 10))
        
        quality_score = (
            coverage_score * weights['coverage'] +
            success_score * weights['success_rate'] +
            critical_score * weights['critical_coverage'] +
            complexity_score * weights['complexity']
        )
        
        return round(quality_score, 1)

    def _check_thresholds(self) -> Dict[str, bool]:
        """Check if quality thresholds are met."""
        return {
            'coverage': self.quality_metrics['coverage_percentage'] >= self.thresholds['min_coverage'],
            'critical_coverage': self.quality_metrics['critical_coverage'] >= self.thresholds['critical_coverage'],
            'success_rate': self.quality_metrics['test_success_rate'] >= self.thresholds['min_success_rate'],
            'complexity': self.quality_metrics['code_complexity'] <= self.thresholds['max_complexity']
        }

    def _generate_quality_report(self, quality_report: Dict):
        """Generate comprehensive quality report."""
        # Save JSON report
        with open('test_quality_report.json', 'w') as f:
            json.dump(quality_report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_quality_report(quality_report)
        
        # Print summary
        self._print_quality_summary(quality_report)

    def _generate_html_quality_report(self, quality_report: Dict):
        """Generate HTML quality report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Quality Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 2em; font-weight: bold; text-align: center; margin: 20px 0; }}
        .good {{ color: #4CAF50; }}
        .warning {{ color: #FF9800; }}
        .critical {{ color: #f44336; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ padding: 15px; border: 1px solid #ddd; border-radius: 5px; text-align: center; }}
        .recommendations {{ background: #e8f4fd; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .recommendation {{ margin: 10px 0; padding: 10px; background: white; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Test Quality Analysis Report</h1>
        <p>Generated: {quality_report['timestamp']}</p>
    </div>
    
    <div class="score {'good' if quality_report['quality_score'] >= 80 else 'warning' if quality_report['quality_score'] >= 60 else 'critical'}">
        Quality Score: {quality_report['quality_score']}/100
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Overall Coverage</h3>
            <p>{quality_report['coverage_analysis']['overall_coverage']:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Critical Coverage</h3>
            <p>{quality_report['coverage_analysis']['critical_coverage']:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Test Success Rate</h3>
            <p>{quality_report['test_analysis']['success_rate']:.1f}%</p>
        </div>
        <div class="metric">
            <h3>Total Tests</h3>
            <p>{quality_report['test_analysis']['total_tests']}</p>
        </div>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
"""
        
        for rec in quality_report['recommendations']:
            html_content += f'<div class="recommendation">{rec}</div>'
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open('test_quality_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _print_quality_summary(self, quality_report: Dict):
        """Print quality summary to console."""
        print(f"\n{'=' * 60}")
        print("TEST QUALITY ANALYSIS SUMMARY")
        print(f"{'=' * 60}")
        
        score = quality_report['quality_score']
        if score >= 80:
            print(f"🎉 Quality Score: {score}/100 (Excellent)")
        elif score >= 60:
            print(f"⚠️  Quality Score: {score}/100 (Good)")
        else:
            print(f"❌ Quality Score: {score}/100 (Needs Improvement)")
        
        print(f"\n📊 Coverage: {quality_report['coverage_analysis']['overall_coverage']:.1f}%")
        print(f"🎯 Critical Coverage: {quality_report['coverage_analysis']['critical_coverage']:.1f}%")
        print(f"✅ Success Rate: {quality_report['test_analysis']['success_rate']:.1f}%")
        print(f"🧪 Total Tests: {quality_report['test_analysis']['total_tests']}")
        
        print(f"\n📋 Top Recommendations:")
        for i, rec in enumerate(quality_report['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        print(f"\n📄 Reports saved:")
        print(f"  - test_quality_report.json")
        print(f"  - test_quality_report.html")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze test quality metrics")
    parser.add_argument('--generate-coverage', action='store_true',
                       help='Generate fresh coverage data before analysis')
    
    args = parser.parse_args()
    
    analyzer = TestQualityAnalyzer()
    
    if args.generate_coverage:
        print("🔄 Generating fresh coverage data...")
        analyzer._generate_coverage_report()
    
    quality_report = analyzer.analyze_test_quality()
    
    # Exit with appropriate code based on quality score
    exit_code = 0 if quality_report['quality_score'] >= 70 else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()