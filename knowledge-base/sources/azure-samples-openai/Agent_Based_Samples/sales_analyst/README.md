<div align="center">
  <h1>
    Sales Analyst AI Agent with Enterprise Security
  </h1>
  <p><strong>Analyze sales and revenue trends to identify prescriptive insights & sales improvement opportunities.</strong></p>
  <br>


https://github.com/user-attachments/assets/4a03cbd5-0fdc-4191-88b2-335da9ef8e1b


</div>

<strong>IMPORTANT NOTE</strong>: Starter templates, instructions, code samples and resources in this Agent_Based_Samples file (“samples”) are designed to assist in accelerating development of agents for specific scenarios. It is important that you review all provided resources and carefully test Agent behavior in the context of your use case: [Learn more](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry-classic).  
 
Certain Agent offerings may be subject to legal and regulatory requirements, may require licenses, or may not be suitable for all industries, scenarios, or use cases. By using any sample, you are acknowledging that Agents or other output created using that sample are solely your responsibility, and that you will comply with all applicable laws, regulations, and relevant safety standards, terms of service, and codes of conduct. 

 

<strong>WARNING</strong>: Sales Analyst is intended to be used only with publicly available data or your own data. Not intended for use with any confidential third-party data. 

## 🚀 Overview

This Azure AI Foundry Agent sample empowers business leaders by helping generate powerful insights for decision-making and helping improve sales efficiency.

This sample is built using Semantic Kernel and can be enabled with Enterprise Security when used with: featuring Azure AI Foundry, Grounding with Bing Search and Azure Databricks. This sample also showcases how to incorporate Responsible AI practices into agents you build by using Azure AI Content Safety.

## 🔍 Business Value

- **Insights for Decision-Making**: Analyzing Sales and Revenue data to provide actionable insights- helping business leaders make informed decisions which drive success.
- **Improving Retail Efficiency**: Build AI agents with the added power of Bing- Use internet insights to identify key sales trends and provide sales improvement strategies- focused on enhancing retail efficiency and sales. Contribute significantly to overall business success and customer satisfaction.
- **Operational Excellence**: Analyze operational data and validate with key sectoral trends to provide opportunities to minimize costs and maximize productivity in business operations.

## 💼 Core Function

- **Trend Summarization of Business KPIs**
  - Granularity of Data: Users can use agents built with this sample to request trend summaries at various levels of granularity, such as weekly, monthly, quarterly, or yearly—based on their needs.
  - Sales Data Trends:  The trend summarization feature provides users with insights into various sales figures (like product SKUs, units sold, pricing, sales, margin & other details) across multiple geographies & regions.

- **Prescriptive Analytics and Internet Insights**
  - Analyzing Trend Data: AI agents built with this sample can  analyze trend data alongside historical figures to understand performance changes over time.
  - Internet Insights powered by Bing: Grounding with Bing search helps identify external factors influencing changes in key performance indicators (KPIs) for your business.

- **Sales & Operational Improvement Recommendations**
  - Identify Improvement Opportunities: The AI agents built with this sample analyze sales and revenue data- combined with internet insights and geographical trends- to provide actionable improvement strategies tailored for each trend.
  - Foresee Expected Outcomes: Analyze and anticipate benefits from each of the proposed actions.

## 🎥 Demo Video



https://github.com/user-attachments/assets/307dd026-3281-4641-92c6-5a38ae997e5b



## ✨ Solution Features

1. **Semantic Kernel and Bring Your Own Azure AI Model:** <br>
Explore the Semantic Kernel Agentic framework to use any Azure AI model tailored for your needs. Allocate tasks to specialized models while optimizing for cost, performance and latency.

2. **World knowledge and internet insights:** <br>
Use Grounding with Bing Search to enhance your agent's knowledge with access to real-time internet insights. This allows the agent to provide up-to-date information and context for better decision-making.

3. **Secure access with Azure Databricks (Genie) Integration:** <br>
Connect your agent to an Azure Databricks workspace for secure, real-time access to structured and unstructured data. Leverage Role-Based Access Control (RBAC) to ensure data security and compliance.

4. **Responsible AI:** <br>
Use Azure AI Content Safety to build robust guardrails for generative AI. Create custom filters for your AI agent which block harmful inputs and outputs.

5. **Agent Observability:** <br>
Analyze usage, performance, and quality against operational Agent benchmarks.


### 🛠️ Technology Stack

| Capability | Technology |
|------------|------------|
| **Orchestration** | Microsoft Semantic Kernel Agent Framework |
| **AI Models** | Azure OpenAI Service (GPT-4o) |
| **Responsible AI** | Azure Content Safety |
| **Internet Insights** | Grounding with Bing Search |
| **Data Security & Lakehouse Intelligence** | Azure Databricks Genie |
| **Observability** | Azure Application Insights, Custom Telemetry |

### Architecture Diagram
![Sales Analyst Architecture](src/solution_accelerators/sales_analyst/docs/images/sales_analyst_architecture_diagram.png)


## 🔧 Getting Started

Ready to deploy Sales Analyst? Follow our comprehensive [Setup Guide](src/solution_accelerators/sales_analyst/SETUP.md) for detailed instructions.

## 📚 Resources

- [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- [Azure AI Foundry](https://ai.azure.com/)

## Sample Datasets
The sample incorporates role-based access control (RBAC) to help you ensure that users have the appropriate level of access to data.
Let's introduce two of our demo user personas: Global Sales Manager (GSM) and Country Sales Manager (CSM):

Global Sales Manager (GSM):
Responsible for overseeing global sales operations across multiple countries and making strategic decisions based on comprehensive data insights.
Sample Dataset: **sample_sales_data_global.csv**. Access to sample sales data for United States and India.

Country Sales Manager (CSM):
Focuses on managing sales operations within one specific country and optimizing its local performance.
Sample Dataset: **sample_sales_data_united_states.csv**. Access to sample sales data for only United States.

Both the sample datasets mentioned above are using synthetic data.
License: Released under CDLA-2.0 (https://cdla.dev/permissive-2-0/).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <p>Developed with ❤️ by Microsoft</p>
</div>