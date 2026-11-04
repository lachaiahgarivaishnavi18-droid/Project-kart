# Deployment and Reproducibility

## Current supported mode

Local Python / GitHub Codespaces Streamlit application. Install `requirements.txt`; run `streamlit run app.py`. The first run generates the deterministic CSV and builds a TF-IDF index in process. There is no external service dependency.

## Optional Azure extension (design only)

The editable deployment diagram illustrates a possible future FastAPI service packaged with Docker, pushed to Azure Container Registry, and deployed to AKS. Terraform could define infrastructure; Azure DevOps could build and deploy; Key Vault would hold credentials; Azure Monitor and Application Insights would collect operational telemetry. Azure AI Search could replace local sparse retrieval, and Azure OpenAI could be an optional explanation provider behind a model interface.

This extension is not implemented or provisioned. It requires a subscription, cost review, approved data handling, identity/access design, network policy, monitoring and incident procedures, and explicit authorization before any resource creation. No paid resources were created.