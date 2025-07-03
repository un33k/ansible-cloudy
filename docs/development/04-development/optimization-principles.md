# CODE OPTIMIZATION PROTOCOL FOR CLAUDE

## MANDATORY OPTIMIZATION FRAMEWORK

### Pre-Implementation Phase
Before writing ANY code, I must:

1. **Analyze Existing Codebase**
   - Search for similar functionality that can be extended
   - Identify reusable patterns and components
   - Map dependencies to avoid duplication

2. **Apply LEVER Principles**
   - **L**ocate: Find existing code that solves similar problems
   - **E**xtend: Build upon existing functionality rather than recreating
   - **V**alidate: Ensure changes maintain backward compatibility
   - **E**nhance: Improve performance while adding features
   - **R**educe: Minimize code footprint and complexity

3. **Score Proposed Solution** (Must score ≥ 7/10)
   - Code reuse potential: /2
   - Maintainability: /2
   - Performance impact: /2
   - Simplicity: /2
   - Test coverage: /2

### Implementation Phase

**Guided Code Generation:**
- Start with the simplest working solution
- Continuously refactor for clarity
- Document trade-offs in comments
- Prefer composition over inheritance
- Use existing utilities and helpers

**Quality Checkpoints:**
- [ ] No duplicate functionality
- [ ] Clear variable/function names
- [ ] Proper error handling
- [ ] Follows project conventions
- [ ] Minimal cyclomatic complexity

### Post-Implementation Review

**Optimization Metrics:**
- Lines of code reduction: Target 30-50% from initial approach
- Function reuse rate: Target >60%
- Test coverage: Target >80%
- Performance baseline: No regression

**Refactoring Triggers:**
- Functions > 20 lines → Split into smaller functions
- Duplicate code blocks > 3 lines → Extract to shared function
- Complex conditionals → Use early returns or strategy pattern
- Nested loops > 2 levels → Consider alternative algorithms

### Continuous Improvement

**For Every Code Block:**
1. Can this extend existing code?
2. Is this the simplest solution?
3. Will this be easy to test?
4. Can this be made more readable?
5. Have I checked for edge cases?

**Documentation Requirements:**
- Why this approach over alternatives
- Performance considerations
- Future extension points
- Known limitations

## IMPLEMENTATION CHECKLIST

Before submitting any code:
- [ ] Searched for existing similar implementations
- [ ] Scored solution ≥ 7/10 on optimization criteria
- [ ] Removed all unnecessary code
- [ ] Added appropriate error handling
- [ ] Followed naming conventions
- [ ] Documented complex logic
- [ ] Considered edge cases
- [ ] Verified no performance regression
- [ ] Checked for security implications
- [ ] Ensured backward compatibility