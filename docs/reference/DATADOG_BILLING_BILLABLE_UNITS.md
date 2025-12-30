# Datadog Billing & Billable Units - LLM Agent Knowledge

## Table of Contents
1. [Infrastructure Monitoring (INFRA)](#infrastructure-monitoring-infra)
2. [APM Billing](#apm-billing)
3. [Serverless Billing](#serverless-billing)
4. [Customer Discovery Questions](#customer-discovery-questions)
5. [Estimation Methods](#estimation-methods)
6. [SKU Reference](#sku-reference)

---

## Infrastructure Monitoring (INFRA)

### Billable Units Overview

**Host Definition**: A host refers to any physical or virtual OS instance being monitored in Datadog. This includes:
- Servers and virtual machines (VMs)
- Nodes within Kubernetes clusters
- Instances within Azure App Service Plans
- Heroku dynos
- AWS EC2 instances
- Google Cloud Platform (GCP) VMs
- Azure VMs
- vSphere VMs

### Billing Methodology

#### VM-Based Infrastructure
- **Metering**: Hosts are tracked hourly throughout the month
- **Billing Calculation**: Uses the **highest count (high-water mark) of the lower 99% of usage hours**
  - Top 1% of usage hours are excluded to mitigate impact of spikes
- **SKU Options**:
  - `HOST-PRO`: Infrastructure Monitoring Pro
  - `HOST-PROPLUS`: Infrastructure Monitoring Pro Plus
  - `HOST-ENT`: Infrastructure Monitoring Enterprise
  - `HOST-BASIC`: Infrastructure Monitoring Basic (lower price, limited features)

#### Kubernetes Infrastructure
- **Billing**: Based on Kubernetes nodes (hosts), not pods or containers
- **Metering**: Same hourly tracking as VM infrastructure
- **Agent Deployment**: Datadog Agent runs as DaemonSet on all Kubernetes nodes
- **Hostname**: Uses the hostname of each k8s node for metering
- **Note**: Container allotment may apply for container monitoring features

### Key Metering Metrics

**Billable Host Detection**:
A host is considered billable if it reports any canonical host IDs from:
- `system.cpu.user` (Agent Hosts)
- `aws.ec2.cpuutilization` (AWS Hosts)
- `gcp.gce.instance.cpu.utilization` (GCP Hosts)
- `azure.vm.percentage_cpu` (Azure Hosts)
- `alibabacloud.ecs.cpu_utilization.average` (Alibaba Hosts)
- `datadog.heroku_agent.running` (Heroku Hosts)
- `vsphere.cpu.usage.avg` (VSphere VMs)
- `otel.datadog_exporter.metrics.running` (OpenTelemetry Hosts)

**Estimated Usage Metric**: `datadog.estimated_usage.hosts[.by_tag]`
- Represents unique hosts seen in the previous 60 minutes
- Includes: regular agent, AWS, GCP, Azure, Alibabacloud, Heroku, OTel, and VSphere hosts
- Does NOT include Azure App Services (known issue)

### Special Cases

**Double-Billing Prevention**:
- VMs with the Agent installed are counted as a single instance
- AWS EC2 instances monitored via AWS integration AND Agent = single billable host
- Hosts marked as non-reporting ("???") do not contribute to billing (may take up to 2 hours to remove)

**Container Allotment**:
- Some infrastructure SKUs include container monitoring allotments
- Fargate tasks do NOT fall under container allotment (separate billing)

---

## APM Billing

### APM Pricing Tiers

| Tier | Annual | Month-to-Month | Hourly | SKU Name |
|------|--------|----------------|--------|----------|
| APM / DevSecOps | $31 / $36 | $36 / $43.20 | $0.06 / $0.072 | `APM-HOST` / `APM-DEVSECOPS` |
| APM Pro / DevSecOps | $35 / $40 | $42 / $48 | $0.07 / $0.08 | `APM-HOST-PRO` / `APM-PRO-DEVSECOPS` |
| APM Enterprise / DevSecOps | $40 / $45 | $48 / $54 | $0.08 / $0.09 | `APM-HOST-ENT` / `APM-ENT-DEVSECOPS` |

**Note**: All APM plans must be sold as an upsell to Infrastructure Monitoring.

### APM Billable Units by Infrastructure Type

#### VM-Based APM
- **Metering Metric**: `datadog.apm.host_instance`
- **Billing**: Per host running APM-instrumented applications
- **Calculation**: Same high-water mark methodology as Infrastructure (99th percentile)
- **Estimated Usage**: `datadog.estimated_usage.apm_hosts[.by_tag]` (unique APM hosts in previous 60 min)

#### Kubernetes APM
- **Metering**: Same as VM-based (per node)
- **Agent**: Datadog Agent runs as DaemonSet on Kubernetes nodes
- **Hostname**: Uses k8s node hostname for metering
- **Note**: Not per-pod billing; billing is at the node level

#### AWS ECS on EC2 APM
- **Metering**: Per EC2 host running ECS tasks
- **Agent**: Deployed as Daemon Service on each EC2 instance
- **Hostname**: Uses underlying EC2 hostname

### APM Span Allotments

**Per APM Host**:
- **Ingested Spans**: 150GB per host (summed across all hosts)
- **Indexed Spans**: 1 million per host (summed across all hosts)

**Overage Pricing**:
- **Ingested Spans**: $0.10 per additional 1GB
- **Indexed Spans**: Varies by retention period (3-180 days), starting at $1.06 per 1M spans (annual, 3-day retention)

---

## Serverless Billing

### Serverless Workload Categories

Datadog categorizes serverless into two main types:
1. **Serverless Functions** (e.g., AWS Lambda)
2. **Serverless Apps** (e.g., AWS Fargate, Azure Container Apps, Google Cloud Run)

### AWS Lambda

#### Infrastructure Monitoring (SERVERLESS_INFRA)
- **SKU**: `SERVERLESS-INFRA` (Serverless Workload Monitoring - Functions)
- **Price**: $5 per active function per month
- **Metering**: Average number of functions per hour across the month
- **Definition**: A function is "active" if it executes one or more times in an hour
- **Calculation**: `(Total hours function was active) / 720 hours * $5`
- **Includes**: 5 Custom Metrics, 15-month metric retention

**Metering Detection**:
- `aws.lambda.invocation` (from AWS integration) OR
- `aws.lambda.enhanced.invocation` (from Lambda extension)

**Distinct Function**: Each combination of AWS account, region, and function name

#### APM (SERVERLESS_APM)
- **SKU**: `SERVERLESS-APM` (Serverless Functions APM)
- **Price**: $10 per 1 million traced invocations per month
- **Metering**: Sum of AWS Lambda invocations connected to APM ingested spans
- **Includes**: 50GB ingested spans, 300K indexed spans per 1M traced invocations
- **Sampling**: Customers can control percentage traced via `DD_TRACE_SAMPLING_RULES`

**Traced Invocation Definition**:
- Trace includes a span named `aws.lambda`
- OR trace includes `@_dd.origin:xray` with `operation_name:aws.lambda.function`

### AWS Fargate

#### Infrastructure Monitoring (FARGATE_INFRA)
- **SKU**: `FARGATE_INFRA` (Fargate Infrastructure Monitoring)
- **Price**: $1.20/month (monthly), $1/month (annual), $1.40/month (on-demand)
- **Metering**: Average concurrent tasks in 5-minute intervals, averaged over the month
- **Definition**: A task is a group of one or more containers running together
- **Note**: Number of containers within a task does NOT affect billing

**Metering Metric**: `datadog.estimated_usage.fargate_tasks[.by_tag]`
- Represents unique Fargate tasks seen in the previous 5 minutes

#### APM (FARGATE_APM)
- **SKU**: `FARGATE_APM` (Fargate APM)
- **Price**: $2.40/month (monthly), $2/month (annual), $2.90/month (on-demand)
- **Metering**: Average concurrent tasks with APM enabled (5-minute intervals)
- **Prerequisite**: Fargate Infrastructure Monitoring required
- **Includes**: 10GB ingested spans, 65K indexed spans per task

**Metering Metric**: `datadog.estimated_usage.apm.fargate_tasks[.by_tag]`

### Azure Serverless

#### Azure App Services
**Infrastructure**:
- **SKU**: `SERVERLESS_APPS` (Serverless Workloads - Apps) OR legacy `INFRA_HOST`
- **Price**: $3 per active app instance per month (SERVERLESS_APPS)
- **Metering**: Active App Service Plan instances
- **Definition**: Counts distinct WebApp `resource_id`s, takes max App Service Plan instances per hour
- **Metric**: `azure.web_serverfarms.current_instance_count` joined with `azure.app_services.count`

**APM**:
- **SKU**: `SERVERLESS_APPS_APM` OR legacy `APM_HOST`
- **Price**: $6 per actively traced app instance per month
- **Metering**: `datadog.serverless.traced_invocations{resource_type:appservice, resource_provider:azure}`

#### Azure Container Apps
**Infrastructure**:
- **SKU**: `SERVERLESS_APPS`
- **Price**: $3 per active app instance per month
- **Metering**: Active Container App replicas
- **Metric**: `azure.app_containerapps.replicas`

**APM**:
- **SKU**: `SERVERLESS_APPS_APM`
- **Price**: $6 per actively traced app instance per month
- **Metering**: `datadog.serverless.traced_invocations{resource_type:containerapp, resource_provider:azure}`

#### Azure Functions
**Infrastructure**:
- **SKU**: `SERVERLESS_APPS`
- **Price**: $3 per active function app instance per month
- **Metering**: Function apps with executions > 0, multiplied by App Service Plan instances (for AAS)

**APM**:
- **SKU**: `SERVERLESS_APPS_APM`
- **Price**: $6 per actively traced function app instance per month
- **Metering**: `datadog.serverless.traced_invocations{resource_type:azurefunction, resource_provider:azure}`

### Google Cloud Serverless

#### Google Cloud Run
**Infrastructure**:
- **SKU**: `SERVERLESS_APPS`
- **Price**: $3 per active app instance per month
- **Metering**: Active Cloud Run container instances
- **Metric**: `gcp.run.container.instance_count{state:active, goog-managed-by:!cloudfunctions}`

**APM**:
- **SKU**: `SERVERLESS_APPS_APM`
- **Price**: $6 per actively traced app instance per month
- **Metering**: `datadog.serverless.traced_invocations{resource_type:cloudrun, resource_provider:gcp}`

#### Google Cloud Functions
**Infrastructure**:
- **SKU**: `SERVERLESS_APPS`
- **Price**: $3 per active function instance per month
- **Metering**: Active Cloud Function instances
- **Metric**: `gcp.cloudfunctions.function.instance_count{state:active}`

**APM**:
- **SKU**: `SERVERLESS_APPS_APM`
- **Price**: $6 per actively traced function instance per month
- **Metering**: `datadog.serverless.traced_invocations{resource_type:cloudfunction, resource_provider:gcp}`

### Serverless Apps Metering Logic

**General Approach**:
- Datadog samples usage in **5-minute intervals**
- Calculates **average number of concurrent active app instances** over the month
- Each distinct app instance observed in an active state during one or more intervals contributes to the monthly average

**Active Instance Definition**:
- **Azure App Services**: Always-on instances (does not scale to zero)
- **Azure Functions**: Instances processing invocations (scales to zero)
- **Azure Container Apps**: Active replicas processing requests (can scale to zero)
- **Google Cloud Run**: Container instances processing requests (scales to zero)
- **Google Cloud Functions**: Function instances processing invocations (scales to zero)

---

## Customer Discovery Questions

### Infrastructure Discovery

**VM/On-Premise Infrastructure**:
1. How many physical servers or VMs do you currently run?
2. What is your typical VM lifecycle? (Always-on vs. ephemeral)
3. Do you use any cloud providers? (AWS, Azure, GCP)
4. How many EC2 instances / Azure VMs / GCP VMs do you have?
5. What is your average vs. peak host count?
6. Do you have separate environments (dev, staging, prod)? How many hosts per environment?

**Kubernetes Discovery**:
1. Are you running Kubernetes? Which distribution? (EKS, GKE, AKS, on-prem)
2. How many Kubernetes clusters do you have?
3. How many nodes per cluster? (This is what gets billed, not pods)
4. What is your node scaling pattern? (Fixed vs. autoscaling)
5. Do you use managed Kubernetes services or self-managed?
6. Are you using any serverless Kubernetes options? (EKS Fargate, GKE Autopilot)

### APM Discovery

**Application Architecture**:
1. How many applications/services do you have?
2. Which languages/frameworks are your applications using?
3. Are your applications containerized? (Docker, Kubernetes)
4. Do you need distributed tracing?
5. What percentage of your infrastructure hosts run applications vs. infrastructure-only?

**APM Requirements**:
1. Do you need error tracking?
2. Do you need performance profiling? (Continuous Profiler)
3. Do you need data streams monitoring? (Kafka, RabbitMQ, etc.)
4. What is your expected trace volume? (spans per second)
5. Do you need long-term trace retention? (affects indexed spans pricing)

### Serverless Discovery

**AWS Lambda**:
1. How many Lambda functions do you have?
2. What is your monthly invocation volume?
3. How many functions are typically active per hour?
4. Do you need APM tracing for Lambda functions?
5. What percentage of invocations do you want to trace? (sampling rate)

**AWS Fargate**:
1. Are you using ECS Fargate or EKS Fargate?
2. How many Fargate tasks/pods do you typically run concurrently?
3. What is your average vs. peak task count?
4. Do your Fargate tasks run continuously or are they ephemeral?
5. Do you need APM for Fargate tasks?

**Azure Serverless**:
1. Are you using Azure App Services? How many app instances?
2. Are you using Azure Container Apps? How many replicas?
3. Are you using Azure Functions? How many function apps?
4. What is your scaling pattern? (Always-on vs. scale-to-zero)
5. Do you need APM for these services?

**Google Cloud Serverless**:
1. Are you using Cloud Run? How many services/instances?
2. Are you using Cloud Functions? How many functions?
3. What is your scaling pattern?
4. Do you need APM for these services?

### General Billing Questions

1. What is your current monitoring solution? (Helps understand current costs)
2. What is your budget range for observability?
3. Do you have predictable usage patterns or highly variable?
4. Are you open to annual commitments for better pricing?
5. Do you need separate billing for different teams/environments?

---

## Estimation Methods

### Infrastructure Host Estimation

#### For Existing Datadog Customers (Trial or Active)
1. **Plan & Usage Page**: `https://app.datadoghq.com/billing/usage?category=infrastructure`
   - Most accurate source (may lag 1-2 days)
   - Shows actual billable usage

2. **Estimated Usage Metric**: `datadog.estimated_usage.hosts[.by_tag]`
   - Real-time estimate (within 10% of actual)
   - Query: `sum:datadog.estimated_usage.hosts{*}`

3. **Infrastructure List**: `https://app.datadoghq.com/infrastructure`
   - Shows current active hosts
   - May include non-billable resources (e.g., load balancers)

#### For Prospects (Not on Datadog)

**AWS**:
- AWS Console → EC2 Dashboard → Running Instances count
- AWS Cost Explorer → Filter by service (EC2)
- CloudWatch: Query `AWS/EC2` namespace metrics

**Azure**:
- Azure Portal → Virtual Machines → Count running VMs
- Azure Cost Management → Filter by resource type

**GCP**:
- GCP Console → Compute Engine → VM Instances count
- GCP Billing → Filter by Compute Engine

**Kubernetes**:
- `kubectl get nodes` (count nodes, not pods)
- Cluster management console → Node count

### APM Host Estimation

#### For Existing Datadog Customers
1. **Plan & Usage Page**: `https://app.datadoghq.com/billing/usage?category=apm`
2. **Estimated Usage Metric**: `datadog.estimated_usage.apm_hosts[.by_tag]`
   - Query: `sum:datadog.estimated_usage.apm_hosts{*}`

#### For Prospects
- Count infrastructure hosts that run applications (not just infrastructure services)
- Estimate: Typically 60-80% of infrastructure hosts run applications
- Ask: "How many of your servers run applications vs. just infrastructure?"

### AWS Lambda Estimation

#### For Existing Datadog Customers
1. **Plan & Usage Page**: `https://app.datadoghq.com/billing/usage?category=serverless`
2. **Metabase Dashboard**: [Serverless Usage Dashboard](https://metabase-analytics.us1.prod.dog/dashboard/35573)
3. **Estimated Usage Metric**: `datadog.estimated_usage.serverless.aws_lambda_functions[.by_tag]`

#### For Prospects - Active Functions Estimation

**CloudWatch Query** (for active functions):
```json
{
    "sparkline": true,
    "metrics": [
        [
            "AWS/Lambda",
            "Invocations",
            {
                "id": "m1"
            }
        ]
    ],
    "view": "singleValue",
    "stacked": false,
    "region": "us-east-1",
    "stat": "Sum",
    "period": 2592000
}
```

**Manual Calculation**:
1. List all Lambda functions in AWS Console
2. For each function, check CloudWatch metrics for hourly invocations
3. Count functions with > 0 invocations per hour
4. Average across the month: `(Sum of hourly active function counts) / 720 hours`

**Note**: CloudWatch limits to 500 time series per query. For >500 functions, use AWS CLI or contact serverless-product@datadoghq.com

#### For Prospects - Traced Invocations Estimation

**CloudWatch Query** (for total invocations):
```json
{
    "sparkline": true,
    "metrics": [
        [
            "AWS/Lambda",
            "Invocations",
            {
                "id": "m1"
            }
        ]
    ],
    "view": "singleValue",
    "stacked": false,
    "region": "us-east-1",
    "stat": "Sum",
    "period": 2592000
}
```

**Calculation Formula**:
```
Total Traced Invocations =
    (Total Lambda Invocations) ×
    (% of functions with APM enabled) ×
    (Sampling Rate)
```

**Example**:
- 100M total invocations
- 40% of functions will have APM enabled
- 25% sampling rate
- Result: 100M × 0.40 × 0.25 = 10M traced invocations = $100/month

### AWS Fargate Estimation

#### For Existing Datadog Customers
1. **Plan & Usage Page**: `https://app.datadoghq.com/billing/usage?category=serverless`
2. **Estimated Usage Metric**: `datadog.estimated_usage.fargate_tasks[.by_tag]`
   - Query: `sum:datadog.estimated_usage.fargate_tasks{*}`

#### For Prospects - Average Concurrent Tasks

**AWS ECS Console Method**:
1. Navigate to ECS Console → Clusters
2. Select all applicable regions
3. For each cluster, view running tasks
4. Record task counts at multiple times throughout the day
5. Calculate average: `(Sum of task counts) / (Number of samples)`

**CloudWatch Metrics Method**:
- Query `AWS/ECS` namespace for `RunningTaskCount` metric
- Average over desired time period (e.g., past 30 days)
- Group by cluster and service

**AWS Cost Management Console**:
- Navigate to Cost Explorer
- Filter by service: ECS
- View Fargate task hours
- Convert to average concurrent tasks: `(Total task hours) / (Hours in period)`

**Example CloudWatch Query** (using AWS CLI):
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name RunningTaskCount \
  --dimensions Name=ClusterName,Value=your-cluster-name \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-31T23:59:59Z \
  --period 300 \
  --statistics Average
```

**Manual Estimation Guide**:
- If customer knows: "We run 20 tasks continuously" → 20 average concurrent tasks
- If customer says: "We scale between 10-50 tasks" → Estimate ~30 average concurrent tasks
- For staging/test environments: Often run 2-4 hours per day → `(Hours per day / 24) × Task count`

### Azure Serverless Estimation

#### Azure App Services
**Infrastructure**:
- Azure Portal → App Services → Count active instances
- Azure Monitor → Query `azure.web_serverfarms.current_instance_count`
- **Quick Graph in Datadog** (if on trial):
  ```
  count_nonzero(default_zero(sum:azure.app_services.cpu_time{*}
    by {instance,name,subscription_id,resource_group}.rollup(sum, 300)))
  ```

**APM**:
- **Quick Graph in Datadog**:
  ```
  count_nonzero(sum:datadog.serverless.traced_invocations{
    resource_provider:azure, resource_type:appservice}
    by {resource_id,instance_id}.as_count().rollup(count, 300))
  ```

#### Azure Container Apps
**Infrastructure**:
- Azure Portal → Container Apps → View replica counts
- Azure Monitor → Query `azure.app_containerapps.replicas`
- **Quick Graph in Datadog**:
  ```
  count_nonzero(default_zero(sum:azure.app_containerapps.replicas{*}
    by {name,subscription_id,resource_group}.rollup(sum, 300)))
  ```

**APM**:
- **Quick Graph in Datadog**:
  ```
  count_nonzero(sum:datadog.serverless.traced_invocations{
    resource_provider:azure, resource_type:containerapp}
    by {resource_id,instance_id}.as_count().rollup(count, 300))
  ```

#### Azure Functions
**Infrastructure**:
- Azure Portal → Function Apps → Count active instances
- Azure Monitor → Query `azure.functions.count` joined with `azure.functions.function_execution_count`
- **Quick Graph in Datadog**:
  ```
  count_nonzero(default_zero(sum:azure.functions.function_execution_count{
    (NOT plan_tier:flexconsumption OR workflowstandard) AND instance:*}
    by {name,instance,subscription_id,resource_group}.as_count().rollup(sum, 300)))
  ```

### Google Cloud Serverless Estimation

#### Google Cloud Run
**Infrastructure**:
- GCP Console → Cloud Run → View active instances per service
- GCP Monitoring → Query `gcp.run.container.instance_count{state:active}`
- **Quick Graph in Datadog**:
  ```
  sum:gcp.run.container.instance_count{state:active}.rollup(avg, 300)
  ```

**APM**:
- **Quick Graph in Datadog**:
  ```
  count_nonzero(sum:datadog.serverless.traced_invocations{
    resource_provider:gcp,resource_type:cloudrun}
    by {resource_id,instance_id}.as_count().rollup(count, 300))
  ```

#### Google Cloud Functions
**Infrastructure**:
- GCP Console → Cloud Functions → View active instances
- GCP Monitoring → Query `gcp.cloudfunctions.function.instance_count{state:active}`
- **Quick Graph in Datadog**:
  ```
  sum:gcp.cloudfunctions.function.instance_count{
    state:active,cloudfunction_generation:gen_1}.rollup(avg, 300)
  ```

### Estimation Best Practices

1. **Use Multiple Data Sources**: Cross-reference CloudWatch/Azure Monitor/GCP Monitoring with customer-provided numbers
2. **Account for Variability**: Ask about peak vs. average usage
3. **Consider All Environments**: Include dev, staging, and production
4. **Account for Growth**: Ask about planned scaling or new projects
5. **Use Trial Period**: If possible, set up a trial to get accurate Datadog usage metrics
6. **Document Assumptions**: Note any assumptions made in estimates

### Common Estimation Pitfalls

1. **Kubernetes**: Counting pods instead of nodes
2. **Fargate**: Using peak task count instead of average concurrent
3. **Lambda**: Counting total functions instead of active functions
4. **Azure App Services**: Counting apps instead of App Service Plan instances
5. **Serverless Apps**: Not accounting for scale-to-zero behavior

---

## SKU Reference

### Infrastructure SKUs

| SKU Code | Product Name | Unit | Typical Use Case |
|----------|--------------|------|------------------|
| `HOST-PRO` | Infrastructure Monitoring Pro | Per host/month | Standard infrastructure monitoring |
| `HOST-PROPLUS` | Infrastructure Monitoring Pro Plus | Per host/month | Advanced infrastructure features |
| `HOST-ENT` | Infrastructure Monitoring Enterprise | Per host/month | Enterprise features + Continuous Profiler |
| `HOST-BASIC` | Infrastructure Monitoring Basic | Per host/month | On-premises hosts with low observability needs |
| `FARGATE_INFRA` | Fargate Infrastructure Monitoring | Per task/month | AWS ECS/EKS Fargate tasks |
| `SERVERLESS_INFRA` | Serverless Workload Monitoring - Functions | Per active function/month | AWS Lambda functions |
| `SERVERLESS_APPS` | Serverless Workloads - Apps | Per app instance/month | Azure App Services, Container Apps, Cloud Run, Cloud Functions |

### APM SKUs

| SKU Code | Product Name | Unit | Typical Use Case |
|----------|--------------|------|------------------|
| `APM-HOST` | APM | Per host/month | Standard APM |
| `APM-HOST-PRO` | APM Pro | Per host/month | APM + Data Streams Monitoring |
| `APM-HOST-ENT` | APM Enterprise | Per host/month | APM Pro + Continuous Profiler |
| `FARGATE_APM` | Fargate APM | Per task/month | APM for Fargate tasks |
| `SERVERLESS_APM` | Serverless Functions APM | Per 1M invocations/month | APM for AWS Lambda |
| `SERVERLESS_APPS_APM` | Serverless Apps APM | Per app instance/month | APM for Azure/GCP serverless apps |

### Special SKU Combinations

**Excluding Fargate** (for mixed workloads):
- `SERVERLESS_APPS_EXCL_FARGATE`: Serverless Apps excluding Fargate
- `SERVERLESS_APPS_APM_EXCL_FARGATE`: Serverless Apps APM excluding Fargate

**Use Case**: When customer has Fargate (grandfathered pricing) + other serverless workloads (new pricing)

---

## Additional Resources

### Internal Datadog Resources
- **APM Pricing FAQs**: Internal Confluence page
- **Serverless Pricing FAQs**: Internal Confluence pages
- **Estimated Usage Metrics Handbook**: Technical documentation
- **Metabase Dashboards**: For usage analysis
  - Serverless Usage: `https://metabase-analytics.us1.prod.dog/dashboard/35573`
  - Serverless Apps Quantity: `https://metabase-analytics.us1.prod.dog/dashboard/84859`

### Customer-Facing Resources
- **Datadog Pricing Page**: `https://www.datadoghq.com/pricing/`
- **Billing Documentation**: `https://docs.datadoghq.com/account_management/billing/`
- **Plan & Usage Page**: `https://app.datadoghq.com/billing/usage`

### Support Channels
- **Sales Pricing Questions**: `#sales-pricing-q_a` Slack channel
- **Serverless Product Team**: `serverless-product@datadoghq.com`
- **Deal Desk**: `deal-desk@datadoghq.com`

---

## Notes for LLM Agents

1. **Always verify SKU availability**: Some SKUs may be region-specific or require approval
2. **Check for grandfathering**: Existing customers may have legacy SKUs that need special handling
3. **Use Plan & Usage as source of truth**: Estimated usage metrics are approximations
4. **Account for bundling**: Some products are bundled (e.g., USM with APM)
5. **Consider volume discounts**: Available for >500 hosts/functions
6. **Document estimation methodology**: Always note how estimates were calculated
7. **Flag uncertainties**: If estimation is difficult, recommend trial period

---

*Last Updated: Based on research from Datadog internal Confluence documentation (December 2025)*
