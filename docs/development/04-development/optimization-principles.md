# CODE OPTIMIZATION PROTOCOL FOR CLAUDE

## CLAUDE-RECOMMENDED DEVELOPMENT PRINCIPLES

### Core Development Philosophy
Based on Claude's official documentation, the following principles guide optimal development:

1. **Direct Integration**
   - Work directly in your development environment
   - Maintain project context awareness
   - Perform real development operations safely

2. **Security-First Approach**
   - Direct API connections without intermediaries
   - Granular permission controls
   - Project-specific configurations

3. **Extended Thinking Methodology**
   - Use "think harder" for complex architectural changes
   - Apply deeper reasoning for debugging intricate issues
   - Create comprehensive implementation plans
   - Evaluate approach tradeoffs systematically

### Workflow Acceleration Techniques

**Understanding Codebases:**
- Start with broad architectural questions
- Identify key patterns and data models
- Map authentication and security mechanisms
- Document findings for team reference

**Code Improvement Process:**
1. Find and fix bugs systematically
2. Refactor legacy code incrementally
3. Add comprehensive test coverage
4. Generate contextual documentation
5. Create detailed pull request descriptions

**Productivity Amplifiers:**
- Use domain-specific language
- Refactor in small, testable increments
- Request explanations alongside code
- Leverage visual analysis for UI/UX
- Control output formats for integration

### Configuration Best Practices

**Settings Hierarchy:**
1. User settings: `~/.claude/settings.json`
2. Project settings: `.claude/settings.json` (shared)
3. Local overrides: `.claude/settings.local.json` (personal)

**Recommended Configurations:**
- Set appropriate tool permissions
- Configure working directory access
- Define output token limits
- Enable/disable specific tools per project
- Implement security hooks

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

## DECISION FRAMEWORK

Before writing any code:
1. Can I extend an existing table? (vs creating new)
2. Can I add to an existing query? (vs new query)
3. Can I enhance an existing hook? (vs new hook)
4. Can I modify an existing component? (vs new component)

### Real Impact

Your trial optimization demonstrates:
- 87% code reduction (1,050 → 140 lines)
- 90% time savings (days → hours)
- 5x performance improvement (single vs multiple queries)
- Zero new tables (extended existing)

These documents incorporate Anthropic's extended thinking methodologies while being specifically tailored to your Convex architecture. They provide both theoretical understanding and practical, actionable guidance that your team can use immediately.

The framework emphasizes:
- Maximum code reuse
- Leveraging Convex's reactivity
- Data locality over normalization
- Computed properties over stored values
- Extension over creation

This will help ensure future features follow the same optimization principles that made your trial flow implementation so successful! 🚀

## CODE GENERATION REQUEST TEMPLATE

When asked to implement [FEATURE]:

### Phase 1: Analysis (MUST COMPLETE FIRST)
- [ ] Read optimization-principles.md
- [ ] Find similar existing patterns
- [ ] Complete complexity assessment
- [ ] Score using Decision Framework

### Phase 2: Implementation
[Only proceed if score > 5]

**Implementation Steps:**
1. Search for reusable components
2. Extend existing code where possible
3. Apply LEVER principles throughout
4. Document decisions inline
5. Refactor iteratively

**Review Requirements:**
- Optimization score calculation
- Performance impact assessment
- Test coverage verification
- Documentation completeness check

## CLAUDE CODE INTEGRATION PRACTICES

### Tool Usage Optimization

**File Operations:**
- Use Read before Edit to understand context
- Batch multiple edits with MultiEdit
- Prefer extending files over creating new ones
- Always verify directory structure with LS

**Search Strategies:**
- Use Task for complex multi-step searches
- Apply Glob for pattern matching
- Leverage Grep for content searches
- Combine tools for comprehensive analysis

**Development Workflows:**
1. **Bug Fixing:**
   - Reproduce issue with test case
   - Search for root cause systematically
   - Fix with minimal code changes
   - Verify fix doesn't break existing tests

2. **Feature Implementation:**
   - Review similar features first
   - Extend existing patterns
   - Add incremental tests
   - Document architectural decisions

3. **Refactoring:**
   - Identify code smells with search tools
   - Refactor in small, verifiable chunks
   - Maintain backward compatibility
   - Update tests alongside changes

### Extended Thinking Application

**When to Use Extended Thinking:**
- Architectural decisions affecting multiple components
- Complex debugging requiring deep analysis
- Performance optimization strategies
- Security vulnerability assessments
- Migration planning for legacy systems

**Extended Thinking Process:**
1. Gather comprehensive context
2. Analyze multiple solution approaches
3. Evaluate tradeoffs systematically
4. Document reasoning for decisions
5. Create implementation roadmap

### Continuous Improvement Metrics

**Track and Optimize:**
- Code reduction percentage per feature
- Time saved through automation
- Test coverage improvements
- Documentation completeness
- Performance benchmarks

**Regular Reviews:**
- Weekly: Code quality metrics
- Monthly: Architecture decisions
- Quarterly: Tool usage patterns
- Annually: Framework effectiveness

This comprehensive framework combines Claude's official recommendations with proven optimization strategies to ensure consistent, high-quality code generation.