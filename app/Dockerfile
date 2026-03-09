# Multi-stage Dockerfile for SaaS Customer Portal
# Stage 1: Build stage
FROM registry.access.redhat.com/ubi9/python-311:latest AS builder

# Set working directory
WORKDIR /app

# Copy requirements file
COPY src/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM registry.access.redhat.com/ubi9/python-311:latest

# Metadata labels
LABEL name="saas-customer-portal" \
      vendor="MCSP" \
      version="1.0.0" \
      summary="SaaS Customer Portal Application" \
      description="A sample SaaS application for MCSP Scenario 1 demonstration" \
      maintainer="platform-team@example.com"

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /opt/app-root/src/.local /opt/app-root/src/.local

# Copy application source code
COPY src/ .

# Create non-root user (if not already present in base image)
USER 1001

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/app-root/src/.local/bin:$PATH \
    PORT=8080

# Expose application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=2)" || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--threads", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "main:app"]