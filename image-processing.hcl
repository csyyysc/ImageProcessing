job "image-processing" {
  datacenters = ["dc1"]

  update {
    max_parallel = 1
    min_healthy_time = "10s"
    healthy_deadline = "3m"
    progress_deadline = "10m"
    auto_revert = true
    auto_promote = true
    canary = 1
  }

  constraint {
    attribute = "${attr.kernel.name}"
    value     = "linux"
  }

  group "backend" {
    count = 1

    network {
      port "image-processing-api" {
        static = 8000
        to = 8000
      }
    }

    task "backend" {
      driver = "docker"

      config {
        image = "ghcr.io/csyyysc/image-processing-backend"
        ports = ["image-processing-api"]
        
        # Mount volumes for data persistence
        volumes = [
          "local/data:/app/data",
          "local/uploads:/app/uploads",
          "local/logs:/app/logs"
        ]
      }

      resources {
        cpu    = 128
        memory = 128
      }

      service {
        name     = "image-processing-backend"
        port     = "image-processing-api"
        provider = "nomad"
        tags     = ["backend", "api", "image-processing"]

        check {
          type     = "http"
          path     = "/health"
          interval = "30s"
          timeout  = "5s"
          check_restart {
            limit = 3
            grace = "30s"
          }
        }
      }
    }
  }

  group "frontend" {
    count = 1

    network {
      port "image-processing" {
        static = 8501
        to = 8501
      }
    }

    task "frontend" {
      driver = "docker"

      config {
        image = "ghcr.io/csyyysc/image-processing-frontend"
        ports = ["image-processing"]
        
        # Environment variables
        env = {
          BACKEND_URL = "http://${NOMAD_IP}:8000"
        }
      }

      resources {
        cpu    = 128
        memory = 128
      }

      service {
        name     = "image-processing-frontend"
        port     = "image-processing"
        provider = "nomad"
        tags     = ["frontend", "web", "streamlit", "image-processing"]

        check {
          type     = "http"
          path     = "/"
          interval = "30s"
          timeout  = "5s"
          check_restart {
            limit = 3
            grace = "30s"
          }
        }
      }
    }
  }
}