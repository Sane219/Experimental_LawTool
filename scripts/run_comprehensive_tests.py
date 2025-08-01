#!/usr/bin/env python3
"""
Comprehensive test runner script for the Legal Document Summarizer.
Executes all test suites with proper reporting and quality metrics.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import argparse
import psutil
from typing import Optional, List, Dict


class ComprehensiveTestRunner:
    """Comprehensive test runner with reporting and quality metrics."""
    
    def __init__(self, verbose=False, coverage=True, parallel=False):
        """Initialize the test runner."""
        self.verbose = verbose
        self.coverage = coverage
        self.parallel = parallel
        self.start_time = None
        self.results = {}
        self.metrics = {
            'start_time': None,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'total_duration': 0.0,
            'peak_memory_mb': 0.0,
            'coverage_percentage': 0.0
        }
        
        # Test suite configuration
        self.test_suites = {
            'unit': {
                'path': 'tests/unit/',
                'description': 'Unit tests for individual components',
                'timeout': 300,
            },
            'integration': {
                'path': 'tests/integration/',
                'description': 'Integration tests for component interaction',
                'timeout': 600,
            },
            'performance': {
                'path': 'tests/performance/',
                'description': 'Performance and scalability tests',
                'timeout': 900,
            },
            'edge_cases': {
                'path': 'tests/edge_cases/',
                'description': 'Edge case and boundary condition tests',
                'timeout': 300,
            },
            'security': {
                'path': 'tests/security/',
                'description': 'Security-focused tests',
                'timeout': 300,
            }
        }
        
        # Quality thresholds
        self.quality_thresholds = {
            'min_coverage': 85.0,
            'critical_coverage': 95.0,
            'max_test_time': 1800,  # 30 minutes
            'max_memory_mb': 2048,
            'min_success_rate': 95.0
        }

    def run_comprehensive_tests(self, suites: Optional[List[str]] = None) -> bool:
        """Run comprehensive test suite with quality metrics."""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        self.start_time = time.time()
        self.metrics['start_time'] = datetime.now().isoformat()
        
        # Initialize results tracking
        self.results = {}
        for suite in self.test_suites.keys():
            self.results[suite] = {
                'success': False,
                'duration': 0.0,
                'test_count': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'memory_usage': 0.0,
                'stdout': '',
                'stderr': ''
            }
        
        # Determine which test suites to run
        if suites is None:
            suites = list(self.test_suites.keys())
        
        overall_success = True
        
        # Run each test suite
        for suite_name in suites:
            print(f"\n📋 Running {suite_name.upper()} tests...")
            success = self._run_test_suite(suite_name)
            if not success:
                overall_success = False
        
        # Check quality thresholds
        quality_passed = self._check_quality_thresholds()
        all_passed = overall_success and quality_passed
        
        # Final summary
        self._print_final_summary(all_passed)
        
        # Generate comprehensive report
        self._generate_comprehensive_report()
        
        return all_passed

    def _run_test_suite(self, suite_name: str) -> bool:
        """Run a specific test suite and collect metrics."""
        suite_config = self.test_suites[suite_name]
        
        # Build pytest command with appropriate options
        cmd = self._build_pytest_command(suite_name, suite_config)
        
        # Monitor resource usage
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024  # MB
        start_time = time.time()
        
        try:
            # Run tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=suite_config['timeout']
            )
            
            # Calculate metrics
            end_time = time.time()
            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            duration = end_time - start_time
            peak_memory = max(start_memory, end_memory)
            
            # Update peak memory tracking
            self.metrics['peak_memory_mb'] = max(
                self.metrics['peak_memory_mb'], peak_memory
            )
            
            # Parse test results
            test_results = self._parse_test_output(result.stdout, result.stderr)
            
            # Store results
            self.results[suite_name] = {
                'success': result.returncode == 0,
                'duration': duration,
                'test_count': test_results['total'],
                'passed': test_results['passed'],
                'failed': test_results['failed'],
                'skipped': test_results['skipped'],
                'memory_usage': peak_memory - start_memory,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Update overall metrics
            self.metrics['total_duration'] += duration
            self.metrics['total_tests'] += test_results['total']
            self.metrics['passed_tests'] += test_results['passed']
            self.metrics['failed_tests'] += test_results['failed']
            self.metrics['skipped_tests'] += test_results['skipped']
            
            # Print suite summary
            self._print_suite_summary(suite_name, self.results[suite_name])
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print(f"❌ {suite_name} tests timed out after {suite_config['timeout']}s")
            self.results[suite_name] = {
                'success': False,
                'duration': suite_config['timeout'],
                'error': f'Timeout after {suite_config["timeout"]}s'
            }
            return False
        except Exception as e:
            print(f"❌ Error running {suite_name} tests: {e}")
            self.results[suite_name] = {
                'success': False,
                'error': str(e)
            }
            return False

    def _build_pytest_command(self, suite_name: str, suite_config: dict) -> List[str]:
        """Build appropriate pytest command with options."""
        cmd = ['python', '-m', 'pytest', suite_config['path']]
        
        # Add common options
        if self.verbose:
            cmd.append('-v')
        
        # Add coverage for unit tests
        if suite_name == 'unit' and self.coverage:
            cmd.extend([
                '--cov=src',
                '--cov-report=xml',
                '--cov-report=html',
                '--cov-report=term-missing'
            ])
        
        # Add parallel execution if requested
        if self.parallel and suite_name in ['unit', 'integration']:
            cmd.extend(['-n', 'auto'])
        
        # Add timeout protection
        cmd.extend(['--timeout', str(suite_config['timeout'] // 2)])
        
        # Add JSON report for parsing
        cmd.extend([
            '--json-report',
            f'--json-report-file=test_results_{suite_name}.json'
        ])
        
        # Suite-specific options
        if suite_name == 'performance':
            cmd.extend(['--benchmark-only', '--benchmark-json=benchmark.json'])
        elif suite_name == 'security':
            cmd.extend(['--maxfail=5'])
        
        return cmd

    def _parse_test_output(self, stdout: str, stderr: str) -> Dict[str, int]:
        """Parse pytest output to extract test counts."""
        results = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        
        # Try to parse from stdout
        lines = stdout.split('\n')
        for line in lines:
            if 'passed' in line and 'failed' in line:
                # Parse line like "5 passed, 2 failed, 1 skipped in 0.5s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        results['passed'] = int(parts[i-1])
                    elif part == 'failed' and i > 0:
                        results['failed'] = int(parts[i-1])
                    elif part == 'skipped' and i > 0:
                        results['skipped'] = int(parts[i-1])
                break
        
        results['total'] = results['passed'] + results['failed'] + results['skipped']
        return results

    def _print_suite_summary(self, suite_name: str, results: dict):
        """Print summary for a test suite."""
        if results['success']:
            print(f"✅ {suite_name.upper()}: {results['passed']} passed, "
                  f"{results['failed']} failed, {results['skipped']} skipped "
                  f"({results['duration']:.1f}s)")
        else:
            print(f"❌ {suite_name.upper()}: FAILED")
            if 'error' in results:
                print(f"   Error: {results['error']}")

    def _check_quality_thresholds(self) -> bool:
        """Check if quality thresholds are met."""
        print(f"\n🎯 Quality Threshold Check")
        print("-" * 40)
        
        all_passed = True
        
        # Success rate check
        if self.metrics['total_tests'] > 0:
            success_rate = (self.metrics['passed_tests'] / self.metrics['total_tests']) * 100
            threshold_met = success_rate >= self.quality_thresholds['min_success_rate']
            status = "✅" if threshold_met else "❌"
            print(f"{status} Success Rate: {success_rate:.1f}% "
                  f"(threshold: {self.quality_thresholds['min_success_rate']}%)")
            if not threshold_met:
                all_passed = False
        
        # Memory usage check
        threshold_met = self.metrics['peak_memory_mb'] <= self.quality_thresholds['max_memory_mb']
        status = "✅" if threshold_met else "❌"
        print(f"{status} Peak Memory: {self.metrics['peak_memory_mb']:.1f}MB "
              f"(threshold: {self.quality_thresholds['max_memory_mb']}MB)")
        if not threshold_met:
            all_passed = False
        
        # Duration check
        threshold_met = self.metrics['total_duration'] <= self.quality_thresholds['max_test_time']
        status = "✅" if threshold_met else "❌"
        print(f"{status} Total Duration: {self.metrics['total_duration']:.1f}s "
              f"(threshold: {self.quality_thresholds['max_test_time']}s)")
        if not threshold_met:
            all_passed = False
        
        return all_passed

    def _print_final_summary(self, success: bool):
        """Print final test summary."""
        print(f"\n{'=' * 60}")
        print(f"Summary:")
        print(f"  Total Tests: {self.metrics['total_tests']}")
        print(f"  Passed: {self.metrics['passed_tests']}")
        print(f"  Failed: {self.metrics['failed_tests']}")
        print(f"  Skipped: {self.metrics['skipped_tests']}")
        print(f"  Duration: {self.metrics['total_duration']:.1f}s")
        print(f"  Peak Memory: {self.metrics['peak_memory_mb']:.1f}MB")
        print(f"{'=' * 60}")
        
        if success:
            print("🎉 COMPREHENSIVE TEST SUITE PASSED")
            print("All tests completed successfully and quality thresholds met!")
        else:
            print("💥 COMPREHENSIVE TEST SUITE FAILED")
            print("Some tests failed or quality thresholds not met.")

    def _generate_comprehensive_report(self):
        """Generate comprehensive test report."""
        # Generate HTML report
        self._generate_html_report()
        
        # Save JSON report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'results': self.results,
            'quality_thresholds': self.quality_thresholds,
            'environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'working_directory': os.getcwd()
            }
        }
        
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📊 Comprehensive report saved to comprehensive_test_report.json")

    def _generate_html_report(self):
        """Generate HTML test report."""
        html_content = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Comprehensive Test Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .metric {{ text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .suite {{ margin: 20px 0; padding: 15px; border-left: 5px solid #4CAF50; }}
            .failure {{ border-left: 5px solid #f44336; }}
            .success {{ color: #4CAF50; }}
            .failed {{ color: #f44336; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Comprehensive Test Report</h1>
            <p>Generated: {datetime.now().isoformat()}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <h3>Total Tests</h3>
                <p>{self.metrics['total_tests']}</p>
            </div>
            <div class="metric">
                <h3>Passed</h3>
                <p class="success">{self.metrics['passed_tests']}</p>
            </div>
            <div class="metric">
                <h3>Failed</h3>
                <p class="failed">{self.metrics['failed_tests']}</p>
            </div>
            <div class="metric">
                <h3>Duration</h3>
                <p>{self.metrics['total_duration']:.1f}s</p>
            </div>
            <div class="metric">
                <h3>Peak Memory</h3>
                <p>{self.metrics['peak_memory_mb']:.1f}MB</p>
            </div>
        </div>
        
        <h2>Test Suite Results</h2>
"""
        
        for suite_name, result in self.results.items():
            success_class = 'success' if result.get('success', False) else 'failure'
            status = '✅ PASSED' if result.get('success', False) else '❌ FAILED'
            suite_name_upper = suite_name.upper()
            
            html_content += f"""
        <div class="suite {success_class}">
            <h3>{suite_name_upper}</h3>
            <p>Status: {status}</p>
            <p>Tests: {result.get('passed', 0)} passed, {result.get('failed', 0)} failed, {result.get('skipped', 0)} skipped</p>
            <p>Duration: {result.get('duration', 0):.1f}s</p>
        </div>
"""
        
        html_content += """
    </body>
</html>
"""
        
        with open('comprehensive_test_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Legal Document Summarizer"
    )
    
    parser.add_argument(
        '--suites', nargs='+', 
        choices=['unit', 'integration', 'performance', 'edge_cases', 'security'],
        help='Specific test suites to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--no-coverage', action='store_true',
        help='Disable coverage reporting'
    )
    parser.add_argument(
        '--parallel', '-p', action='store_true',
        help='Run tests in parallel where possible'
    )
    parser.add_argument(
        '--quick', action='store_true',
        help='Run only unit and integration tests for quick feedback'
    )
    
    args = parser.parse_args()
    
    # Determine test suites to run
    if args.quick:
        suites = ['unit', 'integration']
    elif args.suites:
        suites = args.suites
    else:
        suites = None
    
    # Create and run test runner
    runner = ComprehensiveTestRunner(
        verbose=args.verbose,
        coverage=not args.no_coverage,
        parallel=args.parallel
    )
    
    success = runner.run_comprehensive_tests(suites)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()