# Cloud Orchestration & Automation HLD

## Table of Contents

## Executive Summary

The Cloud Orchestration and Automation program aims at creating standard and automated way to consume cloud services within the Woolworths group.

Key drivers for this program arises from the need to modernize the Woolworths network and software infrastructure fleet to be more elastic to user demands, seasonal and economic factors that are dynamically changing on a daily basis.

In having a unified platform for automating and orchestrating infrastructure, Woolworths will reduce the risk of errors in performing releases and deployments by making the process easily repeatable, testable and consistent.

Benefits of such an undertaking facilitate standard infrastructure to be secure, reliable and improve performance for business needs.

Once established, this program envisions the ability to optimize business units by

- reducing the time to market
- making DevOps practices the norm within the cultural fabric of Woolworths
- establishing an operational excellence practice in the cloud

## Introduction

The goal of this work is to replace manual provisioning process with automation and orchestration available through Self-Service Infrastructure Catalogue for Public Cloud. To achieve this it would be required to create the orchestration workflow that will be processed and completed within a single domain (cloud tenancy). The orchestration workflow will interact with automation workflow in order to use its resulting artefacts as an input components that are going to be used to provide directed action towards cloud providers.

## To-Be Solution Description

![Cloud orchestration - conceptual view](./img/CO-HLD-HL.svg)

Environment that provides automated workflow(s) to test, deploy, monitor and manage cloud tenants hosted with cloud providers. The input criteria for the workflows processes are defined by interface contracts and policies in order to enable automated configuration, coordination, and management of the resources available from the cloud providers.

![COA Solution To-Be](./img/CO-HLD-Flow_HL.svg)

### To-Be Architectural View

![COA Solution To-Be](./img/CO-HLD-COA.svg)

The COA solution would consist of two streams: cloud orchestration and automation (COA) and SOE Image Factory as depicted below. This scope of this document is limited to COA stream.

The COA solution workflow processes incoming JSON data that are being used to generate base repository with the code and components that are going to be be processed by generated Azure DevOps pipeline. The pipeline then create cloud tenancy with all relevant resources based on implementation of input JSON data.

The incoming JSON data are validated against base JSON schema and service catalog offerings. The data then used as an input for the Azure DevOps pipeline to create:

- Repository to host files relevant to the request;
- Terraform module that is created based on service catalog records related to the requested offering;
- Azure DevOps pipeline to create cloud tenancy through Terraform Enterprise and Azure Resource Manager;
- The created Azure DevOps pipeline also being used to create relevant access groups in Active Directory;

### To-Be Solution Overview

The following graph represents proposed high level process to serve as a baseline for proposed solution development and implementation:

![Cloud orchestration - solution overview](./img/CO-HLD-COA_Provisioning.svg)

Once implemented, this solution would require changes in the following areas:

- Onboarding and provisioning practices on organizational level
- Service catalog that would provide items to be used in workflow management software (ServiceNOW)
- Changes to adopt creation and references to the new Service catalog items required for the processing of the requests in the workflow management software(ServiceNOW)
- Processing of the input and output JSON schema as an interface to the solution

#### Applications / Components

| Name| Role |
| --- | --- |
| Azure| Cloud provider |
| Azure DevOps | Cloud Automation platform|
| Azure Resource Manager | Resource Management control plane |
| Repository| Repository to host application deployment files for infrastructure as a code|
| Service Catalog | Publishing service catalog offerings(SCO); mapping SCO's to low level functions;
| ServiceNOW| Digital workflow management platform |
| Terraform Enterprise | Cloud Orchestration platform |

#### Interfaces

| Interface Role | Source App | Target App |
| --- | --- | --- |
| Input JSON schema| ServiceNOW | Azure DevOps |
| Output JSON schema| Azure DevOps | ServiceNOW |
| TFE interface | Azure DevOps | TFE |
| Cloud provider interface | TFE | Cloud provider |

##### Service Catalog

![Cloud orchestration - solution overview](./img/CO-HLD-SC_flow.svg)

The service catalog component os to update service catalog offerings through corresponding JSON schema in Service Now. It also maintains relationships between high level service offerings and low level functions and logical entities.

##### Input/output JSON schema

The input/output Json schemas are to contain in the following information required to process request:

|Root field(L1)|Field(L2)|Description|
|---|---|---|
|productName||The name of the product in the context of the organisation||
||productCode|Code to represent the product capability (3-5 letters)|
||description|Description|What the product functionally does|
||customers|Consumer(s)|Other consuming Products and/or end-users|
||Areas|Tree breakdown of product functional areas (product name is L0)|
|businessArea|Business Area|Internal business area which owns the product|
|productOwners|Product Owner(s)|Individuals from the business area who own the product (can make decisions).|
|costEstimate||Cost Estimate|
|environment||Required environment ( i.e. DEV, TEST, PROD)|
||requiredPlatforms|Platforms|
||monitoring| Required level of monitoring |
||availability| Required availability |
||managed| Mutable/Immutable |
|deliveryEntities|Delivery Entities|All delivery team members should have their own Visual Studio Subscription (if applicable)|
||Name|Name of the entity (internal department or external company)|
||domain|The email domain to whitelist e.g. \domain.com.au\|
||admins|Entity Admins|
|supportEntities||All support team members should have their own Visual Studio Subscription (if applicable)|
||name|Name of the entity (internal department or external company)|
||domain|The email domain to whitelist e.g. \domain.com.au\|
||admins|Entity Admins|

#### Azure DevOps

The role of Azure DevOps is to provide interface between ServiceNow and main request processing pipeline as well as updating Service Catalog inside ServiceNow through JSON schemas. It also provides version control, reporting and automated builds required to handle deployments.

#### Repository

The role of repository is to host all the information relevant to the particular deployment as per service request; It also provides end users with base template files and host Terraform files that are generated based on selected service catalog offering.

#### Managed resources

Managed resources are cloud provider resources available through relevant control plane. The provisioned resources are being mapped through corresponding Terraform modules which being mapped under relevant Service Catalog offering in ServiceNOW.

#### Terraform Enterprise

Terraform Enterprise is a hosted environment that enables users to define and provision a datacenter infrastructure using a high-level configuration language and works as an interface to variety of the cloud providers through relevant control mechanisms.

#### AzureRM

AzureRM(Azure Resource Manager) is a management layer that enables creation, update, and deletion of resources in Azure subscription.

#### Cloud providers

Cloud providers are organisations that provide cloud computing service offerings.

### Other Impacts / Views

This section addresses all the other potential areas of impact, many of which are reflective of non-functional requirements.Most projects which warrant a HLD will impact a high percentage of these areas. The scale of impact will dictate the coverage that needs to be applied and corresponding description of the impact (what and how it will change).Use additional diagrams / views where applicable to support the topic, Reporting; typically associated with the Data view)

Sub-headings have been created below for each of these areas; insert Not Applicable against any area not impacted rather than deleting the heading.

As mentioned earlier, costs/financials are generally best held outside of the HLD as they tend to be more fluid while all the various players / factors are incorporated across the project. If this needs to be included, suggest it be deferred until later stages of the project when the main elements of the project have been agreed (at least in principle).

#### Data retention policy

This content for this section is not available yet.

#### Reporting

This content for this section is not available yet.

#### Infrastructure

Internal and/or external [cloud / hosted], networks, weigh-scales, HSMs, appliances, system landscape / environments etc; see also Capacity, SLAs and Data. A UML-based example of a system landscape and key services is depicted below, Visio-based examples are equally acceptable.

#### Functional

Organizational, key roles, high-level business processes / workflows etc; only call out any of these if the proposed solution reflects or causes a significant change for that element and it has a bearing on the solution in some way ie components, interfaces, infrastructure etc. If well-formed and reasonably stable/complete requirements are available, also consider a requirements traceability matrix (in simple table form) which cross-references grouped (coarse) requirements to the IS capabilities.

#### Security

Identity / role / access management, data security [encryption / masking], segregation of duties, penetration testing etc

#### Governance

Compliance, legislative / regulatory body [eg PCI-DSS, Privacy Act, Consumer Protection], audit controls, loss prevention / fraud etc.

#### Deployment Model

Big bang or phased transition approach etc. An example of a capability roadmap (key capability by domain by year) follows.

#### Accessibility

Portal, mobility, voice, tablets/smart devices etc.

#### Support

Structure of support of all new components (eg Level 1, 2, 3). Scheduling, logs, monitoring, batch controls etc.

#### Capacity

These NFRs are typically supplied along with the Business Requirements, and tabulated into relevant metrics for the Infra team to consume; if a sizing tool is available for a particular domain - eg SAP QuickSizer – the outputs can be inserted / attached / referenced in this document.

#### SLAs

Performance [response times, key processes/reports], high availability / failover, DR, business continuity, backup/restore etc.

#### Ancillary

Decommissioning, document storage, tools, licenses, product end-of-life / sunset date etc.

#### Outside Scope

This content for this section is not available yet.

Any other systems / projects / components outside of this project scope - indirect / adjacent - which may be impacted.

#### Architectural Decisions

Repeat for each architecture decision. Complete as follows:

- Subject Area
- Problem domain / process area within a project. Eg: Store Windows for MSRDC
- Architectural Decision
- This gets completed with the decision result after the decision is made
- Topic
- Project
- AD ID
- Identifier used as reference from the HLD
- Issue or Problem
- Overview of the issue of the problem that needs to be solved
- Assumptions / Assertions
- This is a working area used for documenting assumptions and assertions which contribute to the decision making process. Items can be documented as succinct bullet points. Usually the output of conversations or meetings. Referencing the meetings and dates where assertions are made is good practice, as it can be used to keep contributors accountable in the decision making process
- Motivations
- The reason for needing to make this decision. What is the impact if the decision is not made
- Alternatives
- A succinct list in bullet points of the decision alternatives. If a decision is yet to be made, then this may be an expanded list of options with Pros and Cons and diagrams where necessary to make an informed decision
- Decision
- The final decision, directly copied from the alternative above which was selected
- Justification
- Reason why this decision was made in preference to the other alternatives
- Implications
- What are the impacts or follow on effects of making this decision. Eg: will this decision cause remediation to be needed in some other area or project?
- Derived Requirements
- Any changed business or system requirements as a result of the decision
- Related Decisions
- Reference to any other decisions that were made previously

| Subject Area | Topic | Decision | AD ID | Issue or Problem | Assumptions / Assertions | Motivation(s) | Alternatives | Decision | Justification | Implications | Derived requirements | Related Decisions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Infrastructure Design

This section covers the core infrastructure design that supports the application/ system being delivered.

It should illustrate the generic stack that forms the basis of all deployments (development, test, user acceptance test, performance test, production, dr). The infrastructure differences between these environments will be covered in the Infrastructure Deployments section.

### Key Non-functional requirements

Reference non-functional requirements

### End State Logical Infrastructure

### Design Considerations

This section contains any relevant discussion or commentary on the design.

### Security Considerations

### Operational Considerations

### Monitoring Considerations

### Infrastructure Roles and Identity and Access Management

This section contains the infrastructure roles that are required to build, manage and maintain the system being delivered.

### Deployments required

This section contains design information regarding the specific deployments required e.g. monitoring, security, backup differences etc.

## Infrastructure Deployments

This section contains diagrams for each of the required deployments.
Each section should clearly call out security, monitoring etc required for each individual deployment
