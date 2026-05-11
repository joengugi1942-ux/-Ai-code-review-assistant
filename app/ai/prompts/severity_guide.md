# Severity Guide for Code Review

This guide defines strict criteria for assigning severity levels to issues found during code review. Following these guidelines ensures consistent and actionable output.

## Severity Levels

### CRITICAL (Score: -20)
**Definition**: Security vulnerabilities, data loss risks, or code that will crash/break production.

**Keywords that justify CRITICAL**:
- security, injection, xss, csrf, sqli, leak, vulnerability
- auth, password, secret, token, credential
- crash, segfault, null pointer, deadlock, race condition
- data loss, corruption, transaction rollback

**DO NOT assign CRITICAL** to:
- Style issues
- Performance improvements
- Documentation
- Minor bugs that don't affect functionality

---

### HIGH (Score: -10)
**Definition**: Logic bugs that will cause incorrect behavior, runtime errors, or significant functionality issues.

**Keywords that justify HIGH**:
- bug, error, incorrect, wrong, invalid
- exception, unhandled, missing error handling
- type error, type mismatch, incompatible
- infinite loop, recursion without base case

**Examples**:
- Wrong conditional logic that always executes one branch
- Missing null check causing potential NullPointerException
- Incorrect API usage that returns wrong data

---

### MEDIUM (Score: -5)
**Definition**: Performance issues, maintainability concerns, or code that works but could be improved.

**Keywords that justify MEDIUM**:
- performance, slow, inefficient, bottleneck
- complexity, hard to understand, maintainability
- redundancy, duplication, code smell
- memory leak, resource leak (non-critical)

**Examples**:
- O(n²) algorithm where O(n) is possible
- Unnecessary nested loops
- Missing index in database query

---

### LOW (Score: -1)
**Definition**: Minor issues that don't affect functionality but should be cleaned up.

**Examples**:
- Unused imports or variables
- Minor naming inconsistencies
- Slightly outdated comments
- Small code duplications

---

### INFO (Score: 0)
**Definition**: Suggestions for improvement that are purely advisory.

**Examples**:
- "Consider using a more descriptive variable name"
- "This could be extracted to a utility function"
- "This pattern is deprecated, consider using X instead"

---

## Critical Inflation Prevention

To prevent "critical" inflation:

1. **Only use CRITICAL** for actual security/functional issues
2. If unsure between HIGH and CRITICAL, default to HIGH
3. Request improvements explicitly mention security impact to justify CRITICAL

## Output Format

For each issue, include:
1. **Problem**: What is wrong
2. **Why**: Why it's a problem
3. **Fix**: Concrete suggestion
4. **Severity**: One of: critical, high, medium, low, info