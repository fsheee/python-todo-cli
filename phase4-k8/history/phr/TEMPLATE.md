# PHR: [Topic Title]

**Date**: YYYY-MM-DD
**Author**: [Your Name]
**Status**: [Draft/In Review/Completed]

## Problem Statement

[Describe the problem clearly and concisely. What is happening that shouldn't happen? What should happen that isn't happening?]

### Impact
- [Describe the impact on users, system performance, or other components]
- [Mention severity: Critical/High/Medium/Low]

### Context
- [When does this problem occur?]
- [Under what conditions?]
- [Any relevant error messages or symptoms?]

---

## Hypothesis

[State your hypothesis about the root cause of the problem. What do you think is causing this issue?]

### Hypothesis Details
- [Explain the reasoning behind this hypothesis]
- [What evidence supports this hypothesis?]
- [What evidence would contradict this hypothesis?]

### Proposed Solution
- [Describe the proposed solution]
- [How will this fix the problem?]

---

## Analysis Plan

[How will you test your hypothesis?]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Data Collection
- [What data/logs/metrics will you collect?]
- [How will you measure success?]

### Expected Outcomes
- [What do you expect to see if the hypothesis is correct?]
- [What do you expect to see if the hypothesis is incorrect?]

---

## Review / Conclusion

[Document the results of your analysis]

### Results
- [What actually happened?]
- [Did the results match your expectations?]

### Hypothesis Validated?
- [Yes/No/Partially]

### Final Solution
- [What was the final solution implemented?]
- [Were there any changes from the proposed solution?]

### Lessons Learned
- [What did you learn from this issue?]
- [How can similar issues be prevented in the future?]
- [Any documentation or process improvements needed?]

---

## Related Resources

- [Links to relevant documentation, logs, or other PHRs]
- [References to code files or components]
- [Related issues or tickets]

---

## Skills & Agents Used

### Skills Required for Phase IV

Currently available skills in `.claude/skills/`:
- `explaining-code`: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when user asks "how does this work?"

**Note**: The following skills are **NOT** currently available and would be useful:

### High Priority Skills
- **PHR Generation**: Automated creation of Problem-Hypothesis-Review documents
- **ADR Generation**: Automated creation of Architecture Decision Records

### Medium Priority Skills (Recommended for Phase IV)
- **Kubernetes Manifest Generator**: Generate Kubernetes YAML manifests (Deployment, Service, ConfigMap, Secret, StatefulSet, Ingress)
- **Helm Chart Generator**: Generate Helm chart structure with Chart.yaml and templates
- **Helm Values Validator**: Validate and suggest improvements for values.yaml files
- **Kubernetes Troubleshooter**: Diagnose and suggest fixes for Kubernetes pod/service/ingress issues
- **Minikube Assistant**: Help with Minikube setup, configuration, and common operations

### Low Priority Skills (Nice to Have)
- **Docker Image Builder**: Automated Docker build, tag, and push operations
- **Kubernetes Resource Analyzer**: Analyze Kubernetes resource usage and suggest optimizations
- **Ingress Configuration Helper**: Generate and validate NGINX Ingress configurations
- **PersistentVolume Advisor**: Suggest PVC configurations based on storage requirements

### Agents Required for Phase IV

**Available Agents** (built-in to Claude Code):
- `general-purpose`: For complex, multi-step tasks, code research, and execution
- `Explore`: For exploring codebases, finding files, and understanding structure
- `Plan`: For designing implementation plans and architectural strategies

**Recommended Agent Usage**:
- Use `Explore` agent when: Understanding existing Phase 3 code, finding Dockerfiles, examining directory structures
- Use `Plan` agent when: Designing Helm chart structure, planning Kubernetes resource configurations, creating deployment strategies
- Use `general-purpose` agent when: Building images, troubleshooting deployment issues, executing multi-step setup tasks

### When to Use Skills vs Agents

- **Skills**: Use for specialized tasks (e.g., `/sp.explain-code` to understand Kubernetes YAML)
- **Agents**: Use for autonomous, multi-step work (e.g., "Explore the Phase 3 directory structure and create a deployment plan")

### Skill/Agent Selection for This PHR

- [List which skill(s) were used for this analysis, if any]
- [List which agent(s) were used, if any]
- [Note if any manual work was done without skills/agents]any new