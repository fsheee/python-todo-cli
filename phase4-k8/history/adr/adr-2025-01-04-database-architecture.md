# ADR-001: Database Architecture - External Neon PostgreSQL

## Status
**Accepted** - 2025-01-04

## Context

Phase 4 involves deploying the Todo Chatbot application to Kubernetes (Minikube). The application requires a PostgreSQL database for storing user data, todos, and chat history.

We need to decide between:
1. **Deploying PostgreSQL in Kubernetes** (StatefulSet + PVC)
2. **Using external Neon PostgreSQL** (serverless, cloud-hosted)

### Current State
- Phase 2 and Phase 3 already use **Neon PostgreSQL** (serverless)
- Connection string: `postgresql+asyncpg://user:password@ep-xxx.neon.tech/dbname`
- Database schema and migrations are already set up
- Application is configured for Neon's connection parameters

### Requirements
- Data persistence across pod restarts
- Reliable database availability
- Minimal operational overhead for local development
- Production-ready architecture
- Easy migration path from Phase 3

## Decision

**We will use external Neon PostgreSQL (serverless) and NOT deploy PostgreSQL in Kubernetes.**

### Rationale

**Pros of External Neon PostgreSQL:**
1. **Consistency**: Same database used across Phase 2, 3, and 4
2. **Simplicity**: No StatefulSet, PVC, or storage class configuration needed
3. **Managed Service**: Automatic backups, replication, and high availability
4. **Serverless**: Auto-scales, no capacity planning required
5. **Zero Ops**: No database administration, patching, or maintenance
6. **Cost-Effective**: Pay-per-use pricing, free tier available
7. **Development Speed**: Database already provisioned and configured
8. **Production-Ready**: Battle-tested, reliable infrastructure

**Cons of External Neon PostgreSQL:**
1. **External Dependency**: Requires internet connectivity
2. **Cloud Vendor Lock-in**: Dependent on Neon's availability
3. **Network Latency**: Slightly higher latency than local database (minimal for most use cases)
4. **Cost**: May have costs for production workloads (vs free local PostgreSQL)

**Why NOT PostgreSQL in Kubernetes:**
1. **Complexity**: Requires StatefulSet, PVC, storage classes, and backup strategies
2. **Operational Overhead**: Need to manage database lifecycle, backups, and upgrades
3. **Resource Consumption**: Uses cluster resources (CPU, memory, storage)
4. **Minikube Limitations**: Limited storage and persistence capabilities
5. **Data Loss Risk**: Minikube cluster deletion can lose data if not properly backed up
6. **Inconsistency**: Different database setup than Phase 2/3

## Implementation

### Helm Chart Changes

**No PostgreSQL Resources:**
- ❌ No `postgres-statefulset.yaml`
- ❌ No `postgres-service.yaml`
- ❌ No `postgres-pvc.yaml`

**Backend Configuration:**
- ✅ Add `DATABASE_URL` to backend Secret
- ✅ Connection string points to Neon PostgreSQL
- ✅ Use existing Neon database from Phase 3

### values.yaml Configuration

```yaml
postgres:
  enabled: false  # No PostgreSQL pod deployed
  # Connection string provided via backend.secrets.databaseUrl
```

### Backend Secret

```yaml
backend:
  secrets:
    databaseUrl: "postgresql+asyncpg://user:password@ep-xxx.neon.tech/dbname"
```

## Consequences

### Positive
1. **Faster Deployment**: No database setup or initialization required
2. **Reliable Data**: Neon handles persistence, backups, and replication
3. **Simplified Helm Chart**: Fewer Kubernetes resources to manage
4. **Consistent Environment**: Same database across all phases
5. **Easy Rollback**: Can revert to Phase 3 without data migration

### Negative
1. **Internet Required**: Application requires connectivity to Neon
2. **External Dependency**: System reliability depends on Neon's uptime
3. **Network Latency**: Slight increase in database query latency (typically <50ms)

### Mitigation Strategies

**For Internet Dependency:**
- Use Kubernetes DNS caching
- Implement connection pooling in backend (already configured)
- Add retry logic for transient network failures

**For External Dependency:**
- Monitor Neon's status page
- Have backup connection string for failover (if using multiple regions)
- Consider local PostgreSQL for offline development (optional)

**For Network Latency:**
- Deploy Kubernetes cluster in region close to Neon database
- Use connection pooling to reduce connection overhead
- Implement caching strategies where appropriate

## Alternatives Considered

### Alternative A: PostgreSQL StatefulSet in Kubernetes

**Pros:**
- Self-contained deployment
- No external dependencies
- Lower network latency
- No cloud vendor costs

**Cons:**
- Complex configuration (StatefulSet, PVC, storage classes)
- Backup and restore responsibility
- Resource consumption in cluster
- Different from Phase 2/3 setup
- Data loss risk in Minikube

**Why Rejected:**
- Too complex for local development environment
- Inconsistent with existing Phase 2/3 architecture
- Operational overhead not justified for this use case
- Minikube not suitable for stateful workloads

### Alternative B: SQLite (File-based Database)

**Pros:**
- Zero configuration
- No external dependencies
- Simple file-based storage

**Cons:**
- Not suitable for concurrent access
- No high availability
- Different from Phase 2/3 architecture
- Requires code changes to support

**Why Rejected:**
- Application already designed for PostgreSQL
- Phase 3 uses Neon, changing would require migration
- Not scalable for production use

### Alternative C: Hybrid (Local Dev / Cloud Prod)

**Pros:**
- Best of both worlds
- Local PostgreSQL for development
- Neon for production

**Cons:**
- Environment parity issues
- More complex configuration
- Requires maintaining two setups

**Why Rejected:**
- Unnecessary complexity for this phase
- Minikube is already "development" environment
- External Neon works well for local testing

## Migration Path

**From Phase 3 to Phase 4:**
- No migration required
- Use same Neon database and connection string
- Update `DATABASE_URL` environment variable in backend Secret

**Future: Moving to In-Cluster PostgreSQL (if needed):**
1. Deploy PostgreSQL StatefulSet
2. Export data from Neon: `pg_dump`
3. Import to in-cluster PostgreSQL: `pg_restore`
4. Update `DATABASE_URL` to point to in-cluster service
5. Test application connectivity
6. Switch over backend pods

## References

- **Neon Documentation**: https://neon.tech/docs
- **Kubernetes StatefulSets**: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- **Phase 3 Database Schema**: `../phase3-chatbot/app/database/`
- **Backend Configuration**: `../phase3-chatbot/.env.example`

## Review and Approval

- **Author**: AI Architecture Team
- **Date**: 2025-01-04
- **Reviewed By**: Phase 4 Development Team
- **Status**: Accepted

## Notes

This decision aligns with the project's goal of rapid development and deployment. For production at scale, we may revisit this decision and evaluate:
- Multi-region deployment with regional databases
- Kubernetes Operators (e.g., CloudNativePG, Crunchy PostgreSQL)
- Managed PostgreSQL offerings from cloud providers

For Phase 4 local Minikube deployment, **external Neon PostgreSQL is the optimal choice**.
