# Deployment Guide 🚀

Complete guide to deploying the Banking Assistant in different environments.

---

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Checklist](#production-checklist)

---

## Local Development

### Option A: Automated (Recommended for Windows)

```bash
# Windows only
run.bat
```

This script automatically:
1. ✅ Creates virtual environment
2. ✅ Installs dependencies
3. ✅ Initializes database
4. ✅ Starts Streamlit app

### Option B: Automated (Recommended for Linux/Mac)

```bash
chmod +x run.sh
./run.sh
```

Same automated process as Windows.

### Option C: Manual Setup (All Platforms)

**Step 1: Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Configure API Credentials**
```bash
# Create .env from template
cp .env.example .env
# Edit .env and add your credentials
nano .env  # or use your favorite editor
```

**Step 4: Initialize Database**
```bash
python database_setup.py
```

**Step 5: Run Application**
```bash
streamlit run app.py
```

Application will be available at: **http://localhost:8501**

### Verify Installation

```bash
# Run test suite
python test_crew.py
```

Expected output:
```
✓ All tests passed! System is ready to use.
```

---

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed (optional)

### Option A: Docker Compose (Easiest)

```bash
# 1. Set up environment variables
cp .env.example .env
# 2. Edit .env with your API credentials
nano .env

# 3. Build and start
docker-compose up --build

# 4. Access application
open http://localhost:8501
```

**Useful Commands:**
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild without cache
docker-compose up --build --no-cache

# Run in background
docker-compose up -d
```

### Option B: Docker Only

```bash
# 1. Build image
docker build -t banking-assistant:latest .

# 2. Run container
docker run \
  -p 8501:8501 \
  -e OPENAI_API_KEY="your_api_key" \
  -e OPENAI_API_BASE="https://api.provider.com/v1" \
  -v $(pwd)/bank_data.db:/app/bank_data.db \
  banking-assistant:latest

# 3. Access application
open http://localhost:8501
```

**Environment Variables:**
```bash
docker run \
  -p 8501:8501 \
  -e OPENAI_API_KEY="sk-xxx" \
  -e OPENAI_API_BASE="https://api.together.xyz/v1" \
  -e MAX_RPM="900" \
  -e LOG_LEVEL="INFO" \
  banking-assistant:latest
```

### Push to Docker Hub

```bash
# 1. Tag image
docker tag banking-assistant:latest yourname/banking-assistant:latest

# 2. Login to Docker Hub
docker login

# 3. Push image
docker push yourname/banking-assistant:latest

# 4. Others can now run:
docker run -p 8501:8501 yourname/banking-assistant:latest
```

---

## Cloud Deployment

### Heroku Deployment

**Step 1: Create Heroku App**
```bash
heroku login
heroku create banking-assistant-app
```

**Step 2: Set Environment Variables**
```bash
heroku config:set OPENAI_API_KEY="your_api_key"
heroku config:set OPENAI_API_BASE="https://api.provider.com/v1"
heroku config:set MAX_RPM="900"
```

**Step 3: Create Procfile**
```bash
# Create file named Procfile
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Step 4: Deploy**
```bash
git push heroku main
```

**Access Application:**
```
https://banking-assistant-app.herokuapp.com
```

### AWS Elastic Container Service (ECS)

**Step 1: Build and Push to ECR**
```bash
# Create repository
aws ecr create-repository --repository-name banking-assistant

# Build and push
docker build -t banking-assistant:latest .
docker tag banking-assistant:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/banking-assistant:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/banking-assistant:latest
```

**Step 2: Create ECS Task Definition**
```json
{
  "family": "banking-assistant",
  "containerDefinitions": [
    {
      "name": "banking-assistant",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/banking-assistant:latest",
      "portMappings": [{"containerPort": 8501, "hostPort": 8501}],
      "environment": [
        {"name": "OPENAI_API_KEY", "value": "your_api_key"},
        {"name": "OPENAI_API_BASE", "value": "https://api.provider.com/v1"}
      ],
      "memory": 1024,
      "cpu": 512
    }
  ]
}
```

**Step 3: Create Service**
```bash
aws ecs create-service \
  --cluster default \
  --service-name banking-assistant \
  --task-definition banking-assistant:1 \
  --desired-count 1
```

### Google Cloud Run

**Step 1: Build Image**
```bash
docker build -t banking-assistant:latest .
```

**Step 2: Push to Google Container Registry**
```bash
docker tag banking-assistant:latest gcr.io/PROJECT_ID/banking-assistant
docker push gcr.io/PROJECT_ID/banking-assistant
```

**Step 3: Deploy to Cloud Run**
```bash
gcloud run deploy banking-assistant \
  --image gcr.io/PROJECT_ID/banking-assistant:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY="your_key",OPENAI_API_BASE="https://api.provider.com/v1"
```

---

## Production Checklist

### Security
- [ ] Use environment variables for all secrets (never commit .env)
- [ ] Implement proper authentication/authorization
- [ ] Use HTTPS/TLS for all communications
- [ ] Validate and sanitize all user inputs
- [ ] Set up rate limiting at load balancer level
- [ ] Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
- [ ] Enable database encryption
- [ ] Implement audit logging
- [ ] Set up DDoS protection

### Performance
- [ ] Use a production-grade database (PostgreSQL, not SQLite)
- [ ] Implement caching layer (Redis)
- [ ] Set up CDN for static assets
- [ ] Configure load balancing
- [ ] Set up database connection pooling
- [ ] Implement query optimization
- [ ] Monitor API response times
- [ ] Set up auto-scaling

### Reliability
- [ ] Set up health checks
- [ ] Implement proper error handling and recovery
- [ ] Create backup strategy for database
- [ ] Set up monitoring and alerting
- [ ] Implement logging to centralized service
- [ ] Create incident response plan
- [ ] Set up uptime monitoring
- [ ] Implement graceful shutdown

### Operations
- [ ] Set up CI/CD pipeline
- [ ] Implement automated testing
- [ ] Set up staging environment
- [ ] Create runbooks for common issues
- [ ] Set up log aggregation (ELK, Datadog, etc.)
- [ ] Implement distributed tracing
- [ ] Set up performance monitoring
- [ ] Document deployment process

### API Rate Limiting
- [ ] Verify MAX_RPM setting (900 for Qwen 3.6-27B)
- [ ] Test retry logic under load
- [ ] Monitor for HTTP 429 errors
- [ ] Implement circuit breaker pattern
- [ ] Set up alerts for rate limit hits
- [ ] Document rate limit behavior to users

### Database
- [ ] Migrate from SQLite to PostgreSQL/MySQL
- [ ] Set up database replication
- [ ] Implement automated backups
- [ ] Test disaster recovery
- [ ] Monitor database performance
- [ ] Set up database monitoring alerts

### Monitoring & Alerting

**Key Metrics to Monitor:**
```
- API response time (p50, p95, p99)
- Error rates (4xx, 5xx)
- Rate limit hits (HTTP 429)
- Database query performance
- Memory usage
- CPU usage
- Request throughput (RPS)
- Agent processing time
```

**Alert Thresholds (Suggested):**
```
- Response time > 5s
- Error rate > 1%
- Rate limit hits > 10 per minute
- Memory usage > 80%
- CPU usage > 80%
- Database query > 2s
```

---

## Environment-Specific Configuration

### Development
```bash
LOG_LEVEL=DEBUG
VERBOSE_AGENT_OUTPUT=true
MAX_RPM=900
LLM_TEMPERATURE=0.7
```

### Staging
```bash
LOG_LEVEL=INFO
VERBOSE_AGENT_OUTPUT=false
MAX_RPM=850
LLM_TEMPERATURE=0.7
```

### Production
```bash
LOG_LEVEL=WARNING
VERBOSE_AGENT_OUTPUT=false
MAX_RPM=800
LLM_TEMPERATURE=0.5
```

---

## Troubleshooting Deployments

### Issue: Rate limit errors in production
**Solution:**
```bash
# Reduce MAX_RPM
docker-compose down
# Edit .env: MAX_RPM=700
docker-compose up --build
```

### Issue: Database connection failures
**Solution:**
```bash
# Reinitialize database
python database_setup.py
# Or in Docker:
docker-compose exec banking-assistant python database_setup.py
```

### Issue: Out of memory errors
**Solution:**
```bash
# Increase container memory
# In docker-compose.yml:
services:
  banking-assistant:
    mem_limit: 2g
```

### Issue: API key not being recognized
**Solution:**
```bash
# Verify environment variable
docker-compose exec banking-assistant python config.py
# Check output for "OPENAI_API_KEY: SET"
```

### Issue: Port 8501 already in use
**Solution:**
```bash
# Use different port
docker run -p 8502:8501 banking-assistant:latest
# Or kill process using port
lsof -i :8501
kill -9 <PID>
```

---

## Monitoring & Logging

### View Logs

**Local:**
```bash
tail -f banking_assistant.log
```

**Docker:**
```bash
docker-compose logs -f banking-assistant
```

**Cloud Run:**
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=banking-assistant" --limit 50
```

### Health Check Endpoint

The Streamlit app has a built-in health check at:
```
GET http://localhost:8501/_stcore/health
```

Use in monitoring:
```bash
curl http://localhost:8501/_stcore/health
```

---

## Maintenance

### Regular Tasks

**Daily:**
- [ ] Check error logs
- [ ] Verify uptime
- [ ] Monitor rate limit hits

**Weekly:**
- [ ] Review performance metrics
- [ ] Check database size
- [ ] Verify backups

**Monthly:**
- [ ] Update dependencies
- [ ] Review and optimize slow queries
- [ ] Capacity planning
- [ ] Security audit

### Dependency Updates

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade crewai

# Update all
pip install -r requirements.txt --upgrade

# Rebuild Docker image
docker-compose up --build
```

---

## Support & Resources

- **Documentation**: See README.md and IMPLEMENTATION_SUMMARY.md
- **Quick Start**: See QUICKSTART.md
- **Configuration**: See config.py
- **Testing**: Run test_crew.py
- **Troubleshooting**: See README.md troubleshooting section

---

**Deployment successful!** 🎉

Your Banking Assistant is now running and ready to serve users. Monitor the logs and metrics to ensure smooth operation.
