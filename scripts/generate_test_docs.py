#!/usr/bin/env python3
"""
Test Documentation Generator for the Legal Document Summarizer.
Automatically generates comprehensive documentation for all test suites.
"""

import os
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse


class TestDocumentationGenerator:
    """Generates comprehensive test documentation."""
    
    def __init__(self):
        """Initialize the documentation generator."""
        self.test_info = {}
        self.test_stats = {
            'total_test_files': 0,
            'total_test_functions': 0,
            'total_test_classes': 0,
            'documented_tests': 0,
            'undocumented_tests': 0
        }

    def generate_documentation(self, output_dir: str = 'docs/tests') -> None:
        """Generate comprehensive test documentation."""
        print("📚 Generating Test Documentation")
        print("=" * 50)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Analyze all test files
        self._analyze_test_files()
        
        # Generate documentation files
        self._generate_overview_doc(output_path)
        self._generate_suite_docs(output_path)
        self._generate_coverage_doc(output_path)
        self._generate_maintenance_doc(output_path)
        
        # Generate summary
        self._print_generation_summary()

    def _analyze_test_files(self) -> None:
        """Analyze all test files to extract information."""
        test_dirs = ['unit', 'integration', 'performance', 'edge_cases', 'security']
        
        for test_dir in test_dirs:
            test_path = Path(f'tests/{test_dir}')
            if not test_path.exists():
                continue
                
            self.test_info[test_dir] = {
                'files': [],
                'description': self._get_suite_description(test_dir),
                'total_tests': 0,
                'test_classes': 0
            }
            
            # Analyze each test file
            for test_file in test_path.glob('test_*.py'):
                file_info = self._analyze_test_file(test_file)
                self.test_info[test_dir]['files'].append(file_info)
                self.test_info[test_dir]['total_tests'] += file_info['test_count']
                self.test_info[test_dir]['test_classes'] += file_info['class_count']
                
                self.test_stats['total_test_files'] += 1
                self.test_stats['total_test_functions'] += file_info['test_count']
                self.test_stats['total_test_classes'] += file_info['class_count']
                self.test_stats['documented_tests'] += file_info['documented_count']
                self.test_stats['undocumented_tests'] += file_info['undocumented_count']

    def _analyze_test_file(self, file_path: Path) -> Dict:
        """Analyze a single test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_info = {
                'name': file_path.name,
                'path': str(file_path),
                'docstring': ast.get_docstring(tree) or "No description available",
                'classes': [],
                'functions': [],
                'test_count': 0,
                'class_count': 0,
                'documented_count': 0,
                'undocumented_count': 0,
                'imports': self._extract_imports(tree),
                'fixtures': []
            }
            
            # Analyze classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_test_class(node)
                    file_info['classes'].append(class_info)
                    file_info['class_count'] += 1
                    file_info['test_count'] += class_info['test_count']
                    file_info['documented_count'] += class_info['documented_count']
                    file_info['undocumented_count'] += class_info['undocumented_count']
                    
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        func_info = self._analyze_test_function(node)
                        file_info['functions'].append(func_info)
                        file_info['test_count'] += 1
                        if func_info['docstring']:
                            file_info['documented_count'] += 1
                        else:
                            file_info['undocumented_count'] += 1
                    elif self._is_fixture(node):
                        fixture_info = self._analyze_fixture(node)
                        file_info['fixtures'].append(fixture_info)
            
            return file_info
            
        except Exception as e:
            return {
                'name': file_path.name,
                'path': str(file_path),
                'error': f"Failed to analyze: {e}",
                'test_count': 0,
                'class_count': 0,
                'documented_count': 0,
                'undocumented_count': 0
            }

    def _analyze_test_class(self, node: ast.ClassDef) -> Dict:
        """Analyze a test class."""
        class_info = {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'methods': [],
            'test_count': 0,
            'documented_count': 0,
            'undocumented_count': 0
        }
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                method_info = self._analyze_test_function(item)
                class_info['methods'].append(method_info)
                class_info['test_count'] += 1
                if method_info['docstring']:
                    class_info['documented_count'] += 1
                else:
                    class_info['undocumented_count'] += 1
        
        return class_info

    def _analyze_test_function(self, node: ast.FunctionDef) -> Dict:
        """Analyze a test function."""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'parameters': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list],
            'line_number': node.lineno
        }

    def _analyze_fixture(self, node: ast.FunctionDef) -> Dict:
        """Analyze a pytest fixture."""
        return {
            'name': node.name,
            'docstring': ast.get_docstring(node) or "",
            'scope': self._extract_fixture_scope(node),
            'parameters': [arg.arg for arg in node.args.args]
        }

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _is_fixture(self, node: ast.FunctionDef) -> bool:
        """Check if function is a pytest fixture."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'fixture':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'fixture':
                return True
        return False

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Get decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return "unknown"

    def _extract_fixture_scope(self, node: ast.FunctionDef) -> str:
        """Extract fixture scope."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                for keyword in decorator.keywords:
                    if keyword.arg == 'scope':
                        if isinstance(keyword.value, ast.Constant):
                            return keyword.value.value
        return "function"

    def _get_suite_description(self, suite_name: str) -> str:
        """Get description for test suite."""
        descriptions = {
            'unit': 'Unit tests for individual components and functions',
            'integration': 'Integration tests for component interaction and workflows',
            'performance': 'Performance and scalability tests',
            'edge_cases': 'Edge case and boundary condition tests',
            'security': 'Security-focused tests and vulnerability checks'
        }
        return descriptions.get(suite_name, 'Test suite')

    def _generate_overview_doc(self, output_path: Path) -> None:
        """Generate overview documentation."""
        doc_content = f"""# Test Suite Overview

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics

- **Total Test Files**: {self.test_stats['total_test_files']}
- **Total Test Functions**: {self.test_stats['total_test_functions']}
- **Total Test Classes**: {self.test_stats['total_test_classes']}
- **Documented Tests**: {self.test_stats['documented_tests']}
- **Undocumented Tests**: {self.test_stats['undocumented_tests']}
- **Documentation Coverage**: {(self.test_stats['documented_tests'] / max(self.test_stats['total_test_functions'], 1) * 100):.1f}%

## Test Suites

"""
        
        for suite_name, suite_info in self.test_info.items():
            doc_content += f"""### {suite_name.title()} Tests

{suite_info['description']}

- **Files**: {len(suite_info['files'])}
- **Total Tests**: {suite_info['total_tests']}
- **Test Classes**: {suite_info['test_classes']}

"""
        
        doc_content += """
## Test Organization

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                      # Unit tests
├── integration/               # Integration tests
├── performance/               # Performance tests
├── edge_cases/               # Edge case tests
└── security/                 # Security tests
```

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Suite
```bash
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/performance/   # Performance tests
pytest tests/edge_cases/    # Edge case tests
pytest tests/security/      # Security tests
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run with Markers
```bash
pytest -m "not slow"        # Skip slow tests
pytest -m integration       # Only integration tests
pytest -m performance       # Only performance tests
```

## Quality Standards

- All tests should have descriptive docstrings
- Test functions should follow the naming convention `test_<functionality>_<scenario>`
- Use appropriate fixtures for test setup and teardown
- Mock external dependencies appropriately
- Include both positive and negative test cases
- Maintain test independence (tests should not depend on each other)

## Contributing

When adding new tests:

1. Choose the appropriate test suite directory
2. Follow existing naming conventions
3. Add comprehensive docstrings
4. Include relevant test markers
5. Update this documentation if adding new test categories

"""
        
        with open(output_path / 'overview.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)

    def _generate_suite_docs(self, output_path: Path) -> None:
        """Generate documentation for each test suite."""
        for suite_name, suite_info in self.test_info.items():
            doc_content = f"""# {suite_name.title()} Test Suite

{suite_info['description']}

## Statistics

- **Test Files**: {len(suite_info['files'])}
- **Total Tests**: {suite_info['total_tests']}
- **Test Classes**: {suite_info['test_classes']}

## Test Files

"""
            
            for file_info in suite_info['files']:
                if 'error' in file_info:
                    doc_content += f"""### {file_info['name']}

**Error**: {file_info['error']}

"""
                    continue
                
                doc_content += f"""### {file_info['name']}

{file_info['docstring']}

**Statistics:**
- Tests: {file_info['test_count']}
- Classes: {file_info['class_count']}
- Documented: {file_info['documented_count']}
- Undocumented: {file_info['undocumented_count']}

"""
                
                # Add fixtures if any
                if file_info['fixtures']:
                    doc_content += "**Fixtures:**\n"
                    for fixture in file_info['fixtures']:
                        doc_content += f"- `{fixture['name']}` (scope: {fixture['scope']}): {fixture['docstring'][:100]}...\n"
                    doc_content += "\n"
                
                # Add test classes
                if file_info['classes']:
                    doc_content += "**Test Classes:**\n\n"
                    for class_info in file_info['classes']:
                        doc_content += f"""#### {class_info['name']}

{class_info['docstring']}

**Methods:**
"""
                        for method in class_info['methods']:
                            doc_content += f"- `{method['name']}`: {method['docstring'][:100]}...\n"
                        doc_content += "\n"
                
                # Add standalone test functions
                if file_info['functions']:
                    doc_content += "**Test Functions:**\n\n"
                    for func in file_info['functions']:
                        doc_content += f"""##### {func['name']}

{func['docstring']}

**Parameters:** {', '.join(func['parameters'])}
**Decorators:** {', '.join(func['decorators'])}

"""
            
            with open(output_path / f'{suite_name}_tests.md', 'w', encoding='utf-8') as f:
                f.write(doc_content)

    def _generate_coverage_doc(self, output_path: Path) -> None:
        """Generate test coverage documentation."""
        doc_content = f"""# Test Coverage Analysis

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Documentation Coverage

- **Total Tests**: {self.test_stats['total_test_functions']}
- **Documented Tests**: {self.test_stats['documented_tests']}
- **Undocumented Tests**: {self.test_stats['undocumented_tests']}
- **Documentation Coverage**: {(self.test_stats['documented_tests'] / max(self.test_stats['total_test_functions'], 1) * 100):.1f}%

## Coverage by Suite

"""
        
        for suite_name, suite_info in self.test_info.items():
            total_tests = suite_info['total_tests']
            documented = sum(f.get('documented_count', 0) for f in suite_info['files'])
            coverage = (documented / max(total_tests, 1)) * 100
            
            doc_content += f"""### {suite_name.title()}

- **Total Tests**: {total_tests}
- **Documented**: {documented}
- **Coverage**: {coverage:.1f}%

"""
        
        doc_content += """
## Undocumented Tests

The following tests need documentation:

"""
        
        for suite_name, suite_info in self.test_info.items():
            for file_info in suite_info['files']:
                if 'error' in file_info:
                    continue
                    
                # Check for undocumented functions
                for func in file_info.get('functions', []):
                    if not func['docstring']:
                        doc_content += f"- `{file_info['name']}::{func['name']}` (line {func['line_number']})\n"
                
                # Check for undocumented class methods
                for class_info in file_info.get('classes', []):
                    for method in class_info['methods']:
                        if not method['docstring']:
                            doc_content += f"- `{file_info['name']}::{class_info['name']}::{method['name']}` (line {method['line_number']})\n"

        doc_content += """
## Documentation Standards

### Test Function Documentation

```python
def test_function_behavior_with_valid_input(self):
    \"\"\"Test that function handles valid input correctly.
    
    This test verifies that the function processes valid input
    and returns the expected result without errors.
    \"\"\"
    # Test implementation
```

### Test Class Documentation

```python
class TestDocumentHandler:
    \"\"\"Test suite for DocumentHandler class.
    
    Tests file validation, metadata extraction, and cleanup
    functionality of the DocumentHandler service.
    \"\"\"
    
    def test_validate_file_with_valid_pdf(self):
        \"\"\"Test file validation with a valid PDF file.\"\"\"
        # Test implementation
```

### Fixture Documentation

```python
@pytest.fixture
def sample_document():
    \"\"\"Provide a sample legal document for testing.
    
    Returns a mock legal document with standard content
    that can be used across multiple test functions.
    \"\"\"
    return "Sample legal document content..."
```

"""
        
        with open(output_path / 'coverage.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)

    def _generate_maintenance_doc(self, output_path: Path) -> None:
        """Generate test maintenance documentation."""
        doc_content = f"""# Test Maintenance Guide

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Regular Maintenance Tasks

### Weekly Tasks

1. **Review Test Results**
   - Check CI/CD pipeline results
   - Investigate any failing tests
   - Update test data if needed

2. **Coverage Analysis**
   - Run coverage reports
   - Identify coverage gaps
   - Add tests for uncovered code

3. **Performance Monitoring**
   - Review test execution times
   - Optimize slow tests
   - Update performance benchmarks

### Monthly Tasks

1. **Test Documentation Review**
   - Update test documentation
   - Add missing docstrings
   - Review test organization

2. **Dependency Updates**
   - Update test dependencies
   - Check for security vulnerabilities
   - Test compatibility with new versions

3. **Test Data Maintenance**
   - Update sample documents
   - Refresh test fixtures
   - Clean up temporary test files

### Quarterly Tasks

1. **Test Strategy Review**
   - Evaluate test effectiveness
   - Identify testing gaps
   - Plan new test categories

2. **Performance Benchmarking**
   - Update performance baselines
   - Review scalability tests
   - Optimize resource usage

3. **Security Testing Review**
   - Update security test scenarios
   - Review vulnerability tests
   - Add new attack vectors

## Test Quality Metrics

### Current Metrics

- **Test Count**: {self.test_stats['total_test_functions']}
- **Documentation Coverage**: {(self.test_stats['documented_tests'] / max(self.test_stats['total_test_functions'], 1) * 100):.1f}%
- **Test Files**: {self.test_stats['total_test_files']}

### Target Metrics

- **Code Coverage**: ≥ 85%
- **Critical Component Coverage**: ≥ 95%
- **Test Success Rate**: ≥ 95%
- **Documentation Coverage**: ≥ 90%
- **Test Execution Time**: < 30 minutes

## Common Issues and Solutions

### Flaky Tests

**Problem**: Tests that pass/fail inconsistently
**Solutions**:
- Add proper wait conditions
- Mock time-dependent operations
- Isolate test dependencies
- Use deterministic test data

### Slow Tests

**Problem**: Tests taking too long to execute
**Solutions**:
- Mock external services
- Use smaller test datasets
- Optimize database operations
- Parallelize test execution

### Test Dependencies

**Problem**: Tests failing due to order dependencies
**Solutions**:
- Ensure test isolation
- Use proper setup/teardown
- Avoid shared state
- Use independent test data

### Outdated Tests

**Problem**: Tests not reflecting current functionality
**Solutions**:
- Regular test review cycles
- Update tests with code changes
- Remove obsolete tests
- Add tests for new features

## Best Practices

### Test Organization

1. **Group Related Tests**: Use test classes to group related functionality
2. **Descriptive Names**: Use clear, descriptive test names
3. **Proper Markers**: Use pytest markers for test categorization
4. **Fixture Reuse**: Create reusable fixtures for common setup

### Test Implementation

1. **AAA Pattern**: Arrange, Act, Assert
2. **Single Responsibility**: One test per behavior
3. **Clear Assertions**: Use descriptive assertion messages
4. **Error Testing**: Test both success and failure cases

### Test Data Management

1. **Isolated Data**: Each test should use independent data
2. **Realistic Data**: Use data that reflects real-world scenarios
3. **Data Cleanup**: Clean up test data after execution
4. **Version Control**: Keep test data in version control

## Troubleshooting

### Common Commands

```bash
# Run specific test
pytest tests/unit/test_specific.py::test_function -v

# Run with debugging
pytest tests/unit/test_specific.py --pdb

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Debug Test Failures

1. **Check Test Output**: Review detailed error messages
2. **Use Debugging**: Add breakpoints or print statements
3. **Isolate Issues**: Run individual tests
4. **Check Dependencies**: Verify test environment setup
5. **Review Changes**: Check recent code changes

### Update Test Environment

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-timeout

# Clean test cache
pytest --cache-clear
```

"""
        
        with open(output_path / 'maintenance.md', 'w', encoding='utf-8') as f:
            f.write(doc_content)

    def _print_generation_summary(self) -> None:
        """Print documentation generation summary."""
        print(f"\n{'=' * 60}")
        print("TEST DOCUMENTATION GENERATION COMPLETE")
        print(f"{'=' * 60}")
        
        print(f"📊 Statistics:")
        print(f"  - Test Files Analyzed: {self.test_stats['total_test_files']}")
        print(f"  - Test Functions Found: {self.test_stats['total_test_functions']}")
        print(f"  - Test Classes Found: {self.test_stats['total_test_classes']}")
        print(f"  - Documentation Coverage: {(self.test_stats['documented_tests'] / max(self.test_stats['total_test_functions'], 1) * 100):.1f}%")
        
        print(f"\n📄 Generated Documents:")
        print(f"  - docs/tests/overview.md")
        print(f"  - docs/tests/coverage.md")
        print(f"  - docs/tests/maintenance.md")
        
        for suite_name in self.test_info.keys():
            print(f"  - docs/tests/{suite_name}_tests.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate test documentation")
    parser.add_argument('--output-dir', default='docs/tests',
                       help='Output directory for documentation')
    
    args = parser.parse_args()
    
    generator = TestDocumentationGenerator()
    generator.generate_documentation(args.output_dir)


if __name__ == '__main__':
    main()